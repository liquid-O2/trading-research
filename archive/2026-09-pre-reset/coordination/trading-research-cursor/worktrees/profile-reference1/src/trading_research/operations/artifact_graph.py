"""Finite immutable semantic artifacts above the independent raw byte store.

Only an exact committed manifest is a usable input. The reader is an explicit
instrumentation boundary, not an interceptor of arbitrary Python reads.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from contextlib import contextmanager
from contextvars import ContextVar
from collections.abc import Mapping
import fcntl
import hashlib
import json
import os
from pathlib import Path
from types import MappingProxyType

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import ArtifactRef, ArtifactStore, canonical_json, publish_new
from trading_research.research.folds import Fold, Sample, validate_fold_population
from trading_research.research.temporal_folds import (TemporalDependencyV1, TemporalSampleV1,
    TemporalExclusionV1, TemporalFoldV1, validate_temporal_fold_population,
    validate_dependency_bytes, bounded, DEFAULT_LIMITS, V01V02LimitsV1,
    _validate_temporal_semantics, names as temporal_names)


_READ_OPERATION_MINT = object()
_ACTIVE_READ_OPERATIONS = ContextVar("semantic_active_read_operations", default=())


def _text(value):
    if type(value) is not str or not value or len(value) > 4096:
        raise ContractError("nonempty exact string required")


def _tuple(value, cls=None):
    if type(value) is not tuple or len(value) > 16384 or (cls is not None and any(type(x) is not cls for x in value)):
        raise ContractError("immutable typed tuple required")


def _names(value):
    _tuple(value, str)
    for v in value:
        _text(v)
    if len(set(value)) != len(value):
        raise ContractError("duplicate identity")


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _json(payload):
    if type(payload) is not bytes or len(payload) > 2097152:
        raise ContractError("bounded canonical immutable JSON bytes required")
    try:
        value = json.loads(payload)
        if canonical_json(value) != payload:
            raise ContractError("noncanonical JSON")
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise ContractError("invalid canonical finite JSON") from exc


def payload_ref(payload: bytes, kind="semantic_payload"):
    if type(payload) is not bytes:
        raise ContractError("immutable payload bytes required")
    return ArtifactRef(_sha(payload), len(payload), kind)


@dataclass(frozen=True, slots=True)
class ExecutionIdentity:
    code_ref: ArtifactRef
    configuration_json: bytes
    numerical_settings_json: bytes
    transform_state_refs: tuple[tuple[str, ArtifactRef], ...] = ()

    def __post_init__(self):
        if type(self.code_ref) is not ArtifactRef:
            raise ContractError("retained code reference required")
        if any(type(v) is not bytes or len(v) > 1048576 for v in (self.configuration_json, self.numerical_settings_json)):
            raise ContractError("execution embedded byte bound")
        _json(self.configuration_json)
        numeric = _json(self.numerical_settings_json)
        required = {"backend_id", "precision", "rounding", "seed", "thread_count", "library_versions"}
        if not isinstance(numeric, dict) or set(numeric) != required:
            raise ContractError("complete numerical settings required")
        for key in ("backend_id", "precision", "rounding"):
            _text(numeric[key])
        if type(numeric["thread_count"]) is not int or numeric["thread_count"] < 1:
            raise ContractError("invalid thread count")
        if numeric["seed"] is not None and type(numeric["seed"]) is not int:
            raise ContractError("invalid numerical seed")
        if not isinstance(numeric["library_versions"], dict) or not numeric["library_versions"]:
            raise ContractError("library identities required")
        for k, v in numeric["library_versions"].items():
            _text(k); _text(v)
        _tuple(self.transform_state_refs, tuple)
        if len(self.transform_state_refs)>256: raise ContractError("transform state count bound")
        if any(len(v) != 2 or type(v[1]) is not ArtifactRef for v in self.transform_state_refs):
            raise ContractError("invalid retained transform state")
        _names(tuple(v[0] for v in self.transform_state_refs))
        object.__setattr__(self, "transform_state_refs", tuple(sorted(self.transform_state_refs)))


@dataclass(frozen=True, slots=True)
class DependencyRef:
    slot: str
    source_id: str
    use: str
    columns: tuple[str, ...] = ()

    def __post_init__(self):
        _text(self.slot); _text(self.source_id)
        if type(self.use) is not str or self.use not in {"value", "fit_feature", "fit_label", "definition", "provenance"}:
            raise ContractError("unknown dependency role")
        _names(self.columns)


@dataclass(frozen=True, slots=True)
class RowEvidence:
    row_id: str
    column: str
    source_version: str
    acquisition_id: str
    observed_at: int
    input_known_at: int
    availability_basis: str
    value_json: bytes
    scenario_id: str | None = None
    valid_from: int | None = None
    valid_until: int | None = None

    def __post_init__(self):
        for v in (self.row_id, self.column, self.source_version, self.acquisition_id):
            _text(v)
        timestamp(self.observed_at); timestamp(self.input_known_at)
        if self.observed_at > self.input_known_at:
            raise ContractError("input known before observation")
        if type(self.availability_basis) is not str or self.availability_basis not in {"received", "published", "named_latency_scenario", "derived"}:
            raise ContractError("unknown availability basis")
        if self.availability_basis == "named_latency_scenario":
            _text(self.scenario_id)
        elif self.scenario_id is not None:
            raise ContractError("scenario identity on actual/derived evidence")
        for v in (self.valid_from, self.valid_until):
            if v is not None:
                timestamp(v)
        if self.valid_from is not None and self.valid_until is not None and self.valid_until <= self.valid_from:
            raise ContractError("empty validity interval")
        if type(self.value_json) is not bytes or len(self.value_json) > 1048576:
            raise ContractError("row embedded byte bound")
        _json(self.value_json)

    @property
    def value_hash(self):
        return _sha(self.value_json)


@dataclass(frozen=True, slots=True)
class ValidatedFoldEvidence:
    population: tuple[Sample, ...]
    fold: Fold
    declared_routes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        _tuple(self.population, Sample)
        if len(self.population) > 4096:
            raise ContractError("fold population bound")
        if type(self.fold) is not Fold:
            raise ContractError("typed fold required")
        object.__setattr__(self, "population", tuple(sorted(self.population, key=lambda x: (x.decision_at, x.id))))
        validate_fold_population(self.population, self.fold)
        _tuple(self.declared_routes, tuple)
        if any(len(v) != 2 for v in self.declared_routes):
            raise ContractError("malformed fold route")
        _names(tuple(v[0] for v in self.declared_routes))
        for _, version in self.declared_routes:
            _text(version)
        object.__setattr__(self, "declared_routes", tuple(sorted(self.declared_routes)))


def validate_fold_evidence(population, fold, declared_routes=()):
    return ValidatedFoldEvidence(tuple(population), fold, declared_routes)


@dataclass(frozen=True, slots=True)
class ValidatedTemporalFoldEvidenceV1:
    population: tuple[TemporalSampleV1, ...]
    fold: TemporalFoldV1
    declared_routes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        _tuple(self.population, TemporalSampleV1)
        if len(self.population) > 4096:
            raise ContractError("temporal fold population bound")
        object.__setattr__(self, "population", tuple(sorted(self.population, key=lambda x: (x.decision_at, x.id))))
        _validate_temporal_semantics(self.population, self.fold)
        _tuple(self.declared_routes, tuple)
        if any(len(route) != 2 for route in self.declared_routes):
            raise ContractError("malformed temporal fold route")
        _names(tuple(route[0] for route in self.declared_routes))
        for _, identity in self.declared_routes:
            _text(identity)
        object.__setattr__(self, "declared_routes", tuple(sorted(self.declared_routes)))


def validate_temporal_fold_evidence(population, fold, declared_routes=()):
    return ValidatedTemporalFoldEvidenceV1(
        bounded(population, 4096, "temporal fold population"), fold, declared_routes)


def _temporal_limits(execution):
    if type(execution) is not ExecutionIdentity:
        raise ContractError('temporal fold requires retained execution and local limits')
    config=_json(execution.configuration_json)
    raw=config.get('temporal_limits_v1') if type(config) is dict else None
    if type(raw) is not dict or set(raw)!={f.name for f in fields(V01V02LimitsV1)}:
        raise ContractError('exact adjacent temporal_limits_v1 configuration required')
    return V01V02LimitsV1(**raw)


def _validate_temporal_admission(evidence, execution):
    limits=_temporal_limits(execution)
    result=validate_temporal_fold_population(evidence.population,evidence.fold,limits=limits)
    if len(evidence.declared_routes)>limits.max_oof_edges:
        raise ContractError('temporal declared route capacity exceeded')
    temporal_names(tuple(route[0] for route in evidence.declared_routes),limits.max_oof_edges,limits)
    temporal_names(tuple(dict.fromkeys(route[1] for route in evidence.declared_routes)),limits.max_oof_edges,limits)
    return result,limits


def _validate_fold_evidence(evidence, payloads, execution=None):
    if type(evidence) is ValidatedFoldEvidence:
        return validate_fold_population(evidence.population, evidence.fold)
    if type(evidence) is ValidatedTemporalFoldEvidenceV1:
        result,limits = _validate_temporal_admission(evidence, execution)
        for sample in evidence.population:
            for dependency in sample.dependencies:
                validate_dependency_bytes(dependency, payloads, limits)
        return result
    raise ContractError("exact legacy or temporal fold evidence required")


def sample_target_end(sample):
    if type(sample) is Sample:
        return sample.dependency_end
    if type(sample) is TemporalSampleV1:
        return sample.target_end
    raise ContractError("exact legacy or temporal sample required")


@dataclass(frozen=True, slots=True)
class LabelEvidence:
    row_id: str
    label_node_id: str
    column: str
    target_definition_ref: ArtifactRef

    def __post_init__(self):
        for v in (self.row_id, self.label_node_id, self.column):
            _text(v)
        if type(self.target_definition_ref) is not ArtifactRef:
            raise ContractError("target bytes required")


@dataclass(frozen=True, slots=True)
class FitEvidence:
    fold_node_id: str
    fit_cut: int
    actual_fit_completion_at: int
    training_sample_ids: tuple[str, ...]
    training_groups: tuple[str, ...]
    training_label_refs: tuple[LabelEvidence, ...]
    actual_training_read_manifests: tuple[str, ...]
    target_definition_ref: ArtifactRef

    def __post_init__(self):
        _text(self.fold_node_id)
        timestamp(self.fit_cut); timestamp(self.actual_fit_completion_at)
        if self.actual_fit_completion_at < self.fit_cut:
            raise ContractError("fit completion before fit cut")
        _names(self.training_sample_ids); _names(self.training_groups)
        _tuple(self.training_label_refs, LabelEvidence)
        _names(self.actual_training_read_manifests)
        if max(len(self.training_sample_ids),len(self.training_label_refs),len(self.actual_training_read_manifests))>4096:
            raise ContractError("fit evidence cardinality bound")
        if type(self.target_definition_ref) is not ArtifactRef:
            raise ContractError("fit target required")
        for name in ("training_sample_ids", "training_groups", "actual_training_read_manifests"):
            object.__setattr__(self, name, tuple(sorted(getattr(self, name))))
        object.__setattr__(self, "training_label_refs", tuple(sorted(self.training_label_refs, key=lambda x: (x.row_id, x.column, x.label_node_id))))


@dataclass(frozen=True, slots=True)
class PredictionEvidence:
    row_id: str
    target_definition_ref: ArtifactRef
    target_start: int
    target_end: int
    decision_cut: int
    actual_completion_at: int
    input_known_at: int
    fit_root_id: str
    read_manifest_id: str
    mode: str

    def __post_init__(self):
        for v in (self.row_id, self.fit_root_id, self.read_manifest_id):
            _text(v)
        for v in (self.target_start, self.target_end, self.decision_cut, self.actual_completion_at, self.input_known_at):
            timestamp(v)
        if (self.target_end <= self.target_start or self.actual_completion_at < self.decision_cut
                or self.input_known_at > self.decision_cut or type(self.mode) is not str or self.mode not in {"OOF", "final"}
                or type(self.target_definition_ref) is not ArtifactRef):
            raise ContractError("invalid prediction clocks/target/mode")

    @property
    def known_at(self):
        return max(self.input_known_at, self.actual_completion_at)


@dataclass(frozen=True, slots=True)
class ReadRequest:
    row_id: str
    decision_cut: int
    assembled_at: int
    purpose: str
    schema_id: str
    unit: str
    target_definition_ref: ArtifactRef | None = None
    target_start: int | None = None
    target_end: int | None = None
    date_group: str | None = None
    fold_node_id: str | None = None

    def __post_init__(self):
        for v in (self.row_id, self.schema_id, self.unit):
            _text(v)
        timestamp(self.decision_cut); timestamp(self.assembled_at)
        if self.assembled_at < self.decision_cut or type(self.purpose) is not str or self.purpose not in {"audit", "input", "fit_feature", "fit_label", "OOF", "final"}:
            raise ContractError("invalid read purpose/cut")
        if self.target_definition_ref is not None:
            if type(self.target_definition_ref) is not ArtifactRef:
                raise ContractError("invalid target reference")
            timestamp(self.target_start); timestamp(self.target_end)
            if self.target_end <= self.target_start:
                raise ContractError("empty requested target")
        elif self.target_start is not None or self.target_end is not None:
            raise ContractError("endpoints without target definition")
        for value in (self.date_group,self.fold_node_id):
            if value is not None: _text(value)
        if self.purpose in {"OOF", "fit_feature", "fit_label"}:
            _text(self.date_group); _text(self.fold_node_id)


@dataclass(frozen=True, slots=True)
class ReadBinding:
    column: str
    node_id: str
    source_column: str
    request: ReadRequest
    required: bool = True
    omission_reasons: tuple[str, ...] = ()

    def __post_init__(self):
        for v in (self.column, self.node_id, self.source_column):
            _text(v)
        if type(self.request) is not ReadRequest or type(self.required) is not bool:
            raise ContractError("typed read binding required")
        _names(self.omission_reasons)
        if self.required and self.omission_reasons:
            raise ContractError("required input cannot be optional")
        if not self.required and not self.omission_reasons:
            raise ContractError("optional omission reasons required")


@dataclass(frozen=True, slots=True)
class ReadRecord:
    binding: ReadBinding
    row: RowEvidence

    def __post_init__(self):
        if type(self.binding) is not ReadBinding or type(self.row) is not RowEvidence:
            raise ContractError("typed actual read required")
        if self.row.row_id != self.binding.request.row_id or self.row.column != self.binding.source_column:
            raise ContractError("actual row differs from bound row")


def _coherent_bindings(bindings):
    if not bindings:
        raise ContractError("nonempty actual-read declaration required")
    def identity(r):
        # Units/schema are intentionally per column; all execution routing and
        # original sample/target clocks belong to a single immutable session.
        return (r.row_id, r.decision_cut, r.assembled_at, r.purpose,
                r.target_definition_ref, r.target_start, r.target_end, r.date_group, r.fold_node_id)
    if len({identity(b.request) for b in bindings}) != 1:
        raise ContractError("mixed actual-read session identity")


@dataclass(frozen=True, slots=True)
class ReadManifest:
    namespace: str
    bindings: tuple[ReadBinding, ...]
    reads: tuple[ReadRecord, ...]
    omissions: tuple[tuple[str, str], ...]

    def __post_init__(self):
        _text(self.namespace)
        _tuple(self.bindings, ReadBinding); _tuple(self.reads, ReadRecord); _tuple(self.omissions, tuple)
        if max(len(self.bindings),len(self.reads),len(self.omissions))>128:
            raise ContractError("actual read manifest cardinality bound")
        _names(tuple(b.column for b in self.bindings))
        _coherent_bindings(self.bindings)
        _names(tuple(r.binding.column for r in self.reads))
        if any(len(v) != 2 for v in self.omissions):
            raise ContractError("invalid omission")
        _names(tuple(v[0] for v in self.omissions))
        by = {b.column: b for b in self.bindings}
        seen = {r.binding.column for r in self.reads}
        omitted = dict(self.omissions)
        if seen & omitted.keys() or seen | omitted.keys() != by.keys():
            raise ContractError("all declared inputs require reads or explicit omissions")
        for r in self.reads:
            if r.binding != by[r.binding.column]:
                raise ContractError("actual read configuration changed")
        for c, reason in self.omissions:
            if by[c].required or reason not in by[c].omission_reasons:
                raise ContractError("required/undeclared omission")

    @property
    def id(self):
        return _sha(_encode(self))


KINDS = frozenset({"source", "definition", "measurement", "feature", "label", "fold", "read_manifest", "checkpoint", "transform", "model", "calibrator", "oof_prediction", "final_prediction"})
FITTED = frozenset({"transform", "model", "calibrator"})


@dataclass(frozen=True, slots=True)
class LabelTarget:
    row_id: str
    target_definition_ref: ArtifactRef
    target_start: int
    target_end: int

    def __post_init__(self):
        _text(self.row_id)
        timestamp(self.target_start); timestamp(self.target_end)
        if type(self.target_definition_ref) is not ArtifactRef or self.target_end <= self.target_start:
            raise ContractError("exact retained label target required")


@dataclass(frozen=True, slots=True)
class DerivationEvidence:
    row_id: str
    read_manifest_id: str
    decision_cut: int
    actual_completion_at: int

    def __post_init__(self):
        _text(self.row_id); _text(self.read_manifest_id)
        timestamp(self.decision_cut); timestamp(self.actual_completion_at)
        if self.actual_completion_at < self.decision_cut:
            raise ContractError("derived completion before frozen decision")


@dataclass(frozen=True, slots=True)
class SemanticNodeSpec:
    namespace: str
    logical_key: str
    kind: str
    schema_id: str
    unit: str
    definition_ref: ArtifactRef
    payload_ref: ArtifactRef
    execution: ExecutionIdentity | None = None
    dependencies: tuple[DependencyRef, ...] = ()
    row_evidence: tuple[RowEvidence, ...] = ()
    fit_evidence: FitEvidence | None = None
    prediction_evidence: PredictionEvidence | None = None
    fold_evidence: ValidatedFoldEvidence | None = None
    read_manifest: ReadManifest | None = None
    label_targets: tuple[LabelTarget, ...] = ()
    derivations: tuple[DerivationEvidence, ...] = ()

    def __post_init__(self):
        if type(self.kind) is not str or self.kind not in KINDS:
            raise ContractError("exact semantic kind required")
        _tuple(self.label_targets, LabelTarget); _tuple(self.derivations, DerivationEvidence)
        object.__setattr__(self, "label_targets", tuple(sorted(self.label_targets, key=lambda t:t.row_id)))
        object.__setattr__(self, "derivations", tuple(sorted(self.derivations, key=lambda d:d.row_id)))
        if bool(self.label_targets) != (self.kind == "label"):
            raise ContractError("label role requires retained target endpoints")
        if bool(self.derivations) != (self.kind in {"measurement", "feature"}):
            raise ContractError("computed rows require retained actual derivations")
        if self.kind == "source" and self.dependencies:
            raise ContractError("external source cannot hide computed ancestry")
        for v in (self.namespace, self.logical_key, self.schema_id, self.unit):
            _text(v)
        if type(self.kind) is not str or self.kind not in KINDS or type(self.definition_ref) is not ArtifactRef or type(self.payload_ref) is not ArtifactRef:
            raise ContractError("typed semantic role/content required")
        if self.execution is not None and type(self.execution) is not ExecutionIdentity:
            raise ContractError("typed execution identity required")
        if self.kind not in {"source", "definition", "label", "fold"} and self.execution is None:
            raise ContractError("computed node lacks code/configuration identity")
        _tuple(self.dependencies, DependencyRef); _tuple(self.row_evidence, RowEvidence)
        if len(self.dependencies)>1024: raise ContractError("node dependency count bound")
        row_counts={}
        for row in self.row_evidence: row_counts[row.row_id]=row_counts.get(row.row_id,0)+1
        if len(row_counts)>4096 or max(row_counts.values(),default=0)>128:
            raise ContractError("node row/column count bound before semantic hashing")
        _names(tuple(d.slot for d in self.dependencies))
        object.__setattr__(self, "dependencies", tuple(sorted(self.dependencies, key=lambda d: d.slot)))
        pairs = tuple((r.row_id, r.column) for r in self.row_evidence)
        if len(set(pairs)) != len(pairs):
            raise ContractError("duplicate row/column")
        object.__setattr__(self, "row_evidence", tuple(sorted(self.row_evidence, key=lambda r: (r.row_id, r.column))))
        for present, cls, required in ((self.fit_evidence, FitEvidence, self.kind in FITTED),
                                      (self.prediction_evidence, PredictionEvidence, self.kind in {"oof_prediction", "final_prediction"}),
                                      (self.fold_evidence, (ValidatedFoldEvidence, ValidatedTemporalFoldEvidenceV1), self.kind == "fold"),
                                      (self.read_manifest, ReadManifest, self.kind == "read_manifest")):
            if (present is not None) != required or (present is not None and type(present) not in (cls if type(cls) is tuple else (cls,))):
                raise ContractError("evidence does not match semantic role")
        if self.kind in {"source", "measurement", "feature", "label", "oof_prediction", "final_prediction"} and not self.row_evidence:
            raise ContractError("row evidence required")
        if self.prediction_evidence and (self.prediction_evidence.mode == "OOF") != (self.kind == "oof_prediction"):
            raise ContractError("prediction role mismatch")
        if type(self.fold_evidence) is ValidatedTemporalFoldEvidenceV1:
            _validate_temporal_admission(self.fold_evidence,self.execution)

    @property
    def id(self):
        return _sha(_encode(self))


_RECORDS = {c.__name__: c for c in (ArtifactRef, Sample, Fold, ExecutionIdentity, DependencyRef,
    RowEvidence, ValidatedFoldEvidence, LabelEvidence, FitEvidence, PredictionEvidence,
    ReadRequest, ReadBinding, ReadRecord, ReadManifest, LabelTarget, DerivationEvidence, SemanticNodeSpec,
    TemporalDependencyV1, TemporalSampleV1, TemporalExclusionV1, TemporalFoldV1, ValidatedTemporalFoldEvidenceV1)}


def _primitive(value):
    if is_dataclass(value) and _RECORDS.get(type(value).__name__) is type(value):
        return {"type": type(value).__name__, "fields": {f.name: _primitive(getattr(value, f.name)) for f in fields(value)}}
    if type(value) is tuple:
        return {"tuple": [_primitive(v) for v in value]}
    if type(value) is bytes:
        return {"bytes": value.hex()}
    if value is None or type(value) in (str, int, bool):
        return value
    raise ContractError("unsupported semantic serialization")


def _restore(value):
    if isinstance(value, dict):
        if set(value) == {"tuple"} and isinstance(value["tuple"], list):
            return tuple(_restore(v) for v in value["tuple"])
        if set(value) == {"bytes"} and isinstance(value["bytes"], str):
            return bytes.fromhex(value["bytes"])
        if set(value) == {"type", "fields"} and value["type"] in _RECORDS:
            cls = _RECORDS[value["type"]]
            if not isinstance(value["fields"], dict) or set(value["fields"]) != {f.name for f in fields(cls)}:
                raise ContractError("semantic record field mismatch")
            return cls(**{k: _restore(v) for k, v in value["fields"].items()})
        raise ContractError("unknown semantic envelope")
    if value is None or type(value) in (str, int, bool):
        return value
    raise ContractError("invalid semantic scalar")


def _embedded_bound(value, maximum=2097152):
    # Count without building an encoding or hashing. Bound recursion and container
    # visits as well as raw string/byte lengths before recursive serialization.
    total = 0
    visits = 0
    def walk(v, depth):
        nonlocal total, visits
        visits += 1
        if depth > 48 or visits > 262144:
            raise ContractError("embedded semantic structure bound")
        if type(v) in (str, bytes):
            total += len(v)
        elif type(v) is tuple:
            if len(v) > 16384:
                raise ContractError("embedded semantic tuple bound")
            for x in v: walk(x, depth+1)
        elif is_dataclass(v) and _RECORDS.get(type(v).__name__) is type(v):
            for f in fields(v): walk(getattr(v, f.name), depth+1)
        elif v is None or type(v) in (int, bool):
            total += 8
        else:
            raise ContractError("unregistered embedded semantic value")
        if total > maximum:
            raise ContractError("embedded semantic byte bound")
    walk(value, 0)
    return total


def _encode(value):
    _embedded_bound(value)
    return canonical_json({"format": 1, "value": _primitive(value)})


def _decode(payload):
    value = _json(payload)
    if not isinstance(value, dict) or set(value) != {"format", "value"} or value["format"] != 1:
        raise ContractError("unknown semantic format")
    restored = _restore(value["value"])
    if _encode(restored) != payload:
        raise ContractError("noncanonical typed semantic encoding")
    return restored


@dataclass(frozen=True, slots=True)
class Limits:
    max_nodes_per_commit: int = 256
    max_edges_per_commit: int = 1024
    max_dependency_depth: int = 32
    max_rows_per_node: int = 4096
    max_columns_per_row: int = 128
    max_node_payload_bytes: int = 1048576
    max_manifest_bytes: int = 2097152
    max_store_blob_bytes: int = 33554432
    max_commits: int = 256

    def __post_init__(self):
        if any(type(getattr(self, f.name)) is not int or not 1 <= getattr(self, f.name) <= f.default for f in fields(self)):
            raise ContractError("positive exact finite bounds required")


@dataclass(frozen=True, slots=True)
class ClosureManifest:
    namespace: str
    roots: tuple[str, ...]
    nodes: tuple[SemanticNodeSpec, ...]
    topological_ids: tuple[str, ...]
    edges: int
    depth: int

    _index: object = field(default=None, init=False, repr=False, compare=False)
    _payloads: object = field(default=None, init=False, repr=False, compare=False)
    _limits: object = field(default=None, init=False, repr=False, compare=False)
    _validated: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        _text(self.namespace); _names(self.roots); _names(self.topological_ids)
        _tuple(self.nodes, SemanticNodeSpec)
        if type(self.edges) is not int or self.edges < 0 or type(self.depth) is not int or self.depth < 1:
            raise ContractError("typed closure dimensions required")

    @property
    def by_id(self):
        if self._index is None:
            raise ContractError("closure must be constructed by validation")
        return self._index


_VALIDATED = object()


def _validated_closure(value):
    closure = value.closure if type(value) is VerifiedCommit else value
    if type(closure) is not ClosureManifest or closure._validated is not _VALIDATED:
        raise ContractError("validated closure evidence required")
    return closure


def _references(node):
    refs = [node.definition_ref, node.payload_ref]
    if node.execution:
        refs.append(node.execution.code_ref)
        refs.extend(v for _, v in node.execution.transform_state_refs)
    if node.fit_evidence:
        refs.append(node.fit_evidence.target_definition_ref)
        refs.extend(v.target_definition_ref for v in node.fit_evidence.training_label_refs)
    if node.prediction_evidence:
        refs.append(node.prediction_evidence.target_definition_ref)
    if node.read_manifest:
        refs.extend(b.request.target_definition_ref for b in node.read_manifest.bindings if b.request.target_definition_ref)
    refs.extend(t.target_definition_ref for t in node.label_targets)
    if type(node.fold_evidence) is ValidatedTemporalFoldEvidenceV1:
        refs.extend(d.evidence_ref for s in node.fold_evidence.population for d in s.dependencies)
    return tuple(refs)


def _row(node, row_id, column):
    matches = [r for r in node.row_evidence if r.row_id == row_id and r.column == column]
    if len(matches) != 1:
        raise DependencyUnavailable("exact row/column absent")
    return matches[0]


def _admit_node_sizes(node_specs,limits):
    if not node_specs or len(node_specs)>limits.max_nodes_per_commit:
        raise ContractError("pre-hash semantic node count bound")
    for n in node_specs:
        _embedded_bound(n, limits.max_manifest_bytes)
        counts = {}
        for r in n.row_evidence:
            counts[r.row_id] = counts.get(r.row_id, 0) + 1
        if len(counts) > limits.max_rows_per_node or max(counts.values(), default=0) > limits.max_columns_per_row:
            raise ContractError("pre-hash row/column bound")
        if n.fold_evidence and len(n.fold_evidence.population) > limits.max_rows_per_node:
            raise ContractError("configured fold population bound")
        if n.read_manifest and len(n.read_manifest.bindings) > limits.max_columns_per_row:
            raise ContractError("configured actual-read bound")


def validate_closure(roots, node_specs, verified_payloads, namespace, limits=Limits()):
    if type(limits) is not Limits:
        raise ContractError("typed closure limits required")
    _text(namespace); _names(roots); _tuple(node_specs, SemanticNodeSpec)
    if not isinstance(verified_payloads, Mapping) or len(verified_payloads)>max(1,limits.max_manifest_bytes//16):
        raise ContractError("bounded retained payload mapping required")
    verified_payloads = dict(verified_payloads)
    if not roots or not node_specs or len(node_specs) > limits.max_nodes_per_commit:
        raise ContractError("empty/excessive semantic closure")
    _admit_node_sizes(node_specs,limits)
    by = {n.id: n for n in node_specs}
    if len(by) != len(node_specs) or len({n.logical_key for n in node_specs}) != len(node_specs):
        raise ContractError("duplicate semantic/logical identity")
    if any(n.namespace != namespace for n in node_specs):
        raise ContractError("cross-namespace closure")
    edges = sum(len(n.dependencies) for n in node_specs)
    if edges > limits.max_edges_per_commit:
        raise ContractError("edge bound")
    visiting, depths, order = set(), {}, []
    def visit(identity):
        if identity in visiting or identity not in by:
            raise ContractError("cycle or missing declared dependency")
        if identity in depths:
            return depths[identity]
        if len(visiting) >= limits.max_dependency_depth:
            raise ContractError("dependency depth bound")
        visiting.add(identity)
        depth = 1 + max((visit(d.source_id) for d in by[identity].dependencies), default=0)
        visiting.remove(identity)
        if depth > limits.max_dependency_depth:
            raise ContractError("dependency depth bound")
        depths[identity] = depth; order.append(identity)
        return depth
    for identity in sorted(roots):
        visit(identity)
    if set(depths) != set(by):
        raise ContractError("unreachable undeclared extra nodes")
    closure = ClosureManifest(namespace, tuple(sorted(roots)), tuple(by[i] for i in sorted(by)), tuple(order), edges, max(depths.values()))
    object.__setattr__(closure, "_index", MappingProxyType(by))
    object.__setattr__(closure, "_payloads", MappingProxyType(dict(verified_payloads)))
    object.__setattr__(closure, "_limits", limits)
    # Internal validation may traverse an earlier topological fitted node; public
    # evidence is certified only after the entire validation loop returns.
    for identity in closure.topological_ids:
        node = by[identity]
        counts = {}
        for row in node.row_evidence:
            counts[row.row_id] = counts.get(row.row_id, 0) + 1
        if len(counts) > limits.max_rows_per_node or max(counts.values(), default=0) > limits.max_columns_per_row:
            raise ContractError("row/column bound")
        for ref in _references(node):
            if type(ref) is not ArtifactRef or type(ref.kind) is not str or not ref.kind:
                raise ContractError("typed retained reference required")
            if ref.size_bytes > limits.max_node_payload_bytes:
                raise ContractError("payload bound")
            if ref.sha256 not in verified_payloads:
                raise DependencyUnavailable("required retained bytes absent")
            raw = verified_payloads[ref.sha256]
            if type(raw) is not bytes or len(raw) != ref.size_bytes or _sha(raw) != ref.sha256:
                raise IntegrityError("referenced bytes disagree")
        if node.row_evidence:
            expected = canonical_json([[r.row_id, r.column, _json(r.value_json)] for r in node.row_evidence])
            if verified_payloads[node.payload_ref.sha256] != expected:
                raise IntegrityError("row field hashes differ from retained payload")
        for dep in node.dependencies:
            source = by[dep.source_id]
            if source.kind == "label" and dep.use not in {"fit_label", "provenance"}:
                raise ContractError("label in feature/value path")
            if dep.use == "fit_label" and (source.kind != "label" or node.kind not in FITTED):
                raise ContractError("labels require an explicit fit consumer")
            if dep.use == "fit_feature" and source.kind == "final_prediction":
                raise ContractError("final predictions cannot train downstream fits")
            if dep.columns and not set(dep.columns) <= {r.column for r in source.row_evidence}:
                raise ContractError("unknown dependency column")
        ancestors = _ancestors(node.id, by)
        if node.kind in {"source", "measurement", "feature"} and any(by[i].kind in FITTED or by[i].kind == "label" for i in ancestors):
            raise ContractError("hidden fitted dependency in fold-independent row")
        if node.label_targets:
            targets = {t.row_id: t for t in node.label_targets}
            if len(targets) != len(node.label_targets) or set(targets) != {r.row_id for r in node.row_evidence}:
                raise ContractError("exact label row target coverage required")
            for row in node.row_evidence:
                if row.observed_at != targets[row.row_id].target_end or row.input_known_at < targets[row.row_id].target_end:
                    raise ContractError("label row precedes retained target maturity")
        if node.derivations:
            _validate_derivations(node, closure)
        if node.fold_evidence:
            _validate_fold_evidence(node.fold_evidence, verified_payloads, node.execution)
        if node.read_manifest:
            _validate_read_manifest(node, closure)
        if node.fit_evidence:
            _validate_fit(node, closure)
        if node.prediction_evidence:
            _validate_prediction(node, closure)
    object.__setattr__(closure, "_payloads", MappingProxyType({r.sha256:verified_payloads[r.sha256] for n in closure.nodes for r in _references(n)}))
    object.__setattr__(closure, "_validated", _VALIDATED)
    return closure


def _ancestors(identity, by):
    seen, todo = set(), [identity]
    while todo:
        i = todo.pop()
        if i in seen:
            continue
        if i not in by:
            raise ContractError("missing ancestor")
        seen.add(i)
        todo.extend(d.source_id for d in by[i].dependencies)
    return seen


def _validate_fit(node, closure):
    by = closure.by_id; fit = node.fit_evidence
    ancestors = _ancestors(node.id, by)
    if fit.fold_node_id not in ancestors or by[fit.fold_node_id].kind != "fold":
        raise ContractError("fit lacks retained fold dependency")
    evidence = by[fit.fold_node_id].fold_evidence
    fold = evidence.fold
    population = {s.id: s for s in evidence.population}
    expected_groups = tuple(sorted({population[i].date_group for i in fold.training_ids}))
    if (not fold.training_ids or tuple(sorted(fit.training_sample_ids)) != tuple(sorted(fold.training_ids))
            or tuple(sorted(fit.training_groups)) != expected_groups or fit.fit_cut != fold.fit_at):
        raise ContractError("fit training membership differs from validated fold")
    if {l.row_id for l in fit.training_label_refs} != set(fold.training_ids) or len(fit.training_label_refs) != len(fold.training_ids):
        raise ContractError("complete exact training labels required")
    for dependency in node.dependencies:
        source = by[dependency.source_id]
        if source.kind not in FITTED | {"fold","read_manifest","definition","label"}:
            raise ContractError("fitted state bypasses actual training read manifests")
        if source.kind == "label" and dependency.use != "fit_label":
            raise ContractError("unreconciled label provenance on fitted state")
    expected_labels = {l.label_node_id for l in fit.training_label_refs}
    if {d.source_id for d in node.dependencies if d.use == "fit_label"} != expected_labels:
        raise ContractError("extra or missing actual fit-label dependency")
    if {d.source_id for d in node.dependencies if by[d.source_id].kind == "read_manifest"} != set(fit.actual_training_read_manifests):
        raise ContractError("extra or missing actual training-read dependency")
    for label in fit.training_label_refs:
        if label.label_node_id not in ancestors or by[label.label_node_id].kind != "label":
            raise ContractError("training label absent from closure")
        if not any(d.source_id == label.label_node_id and d.use == "fit_label" for d in node.dependencies):
            raise ContractError("training label requires direct fit-label edge")
        row = _row(by[label.label_node_id], label.row_id, label.column)
        if row.input_known_at > fit.fit_cut or label.target_definition_ref != fit.target_definition_ref:
            raise ContractError("future or wrong-target training label")
        sample = population[label.row_id]
        target = next((t for t in by[label.label_node_id].label_targets if t.row_id == label.row_id), None)
        if (target is None or target.target_definition_ref != label.target_definition_ref
                or target.target_start != sample.decision_at or target.target_end != sample_target_end(sample)
                or row.input_known_at != sample.label_known_at):
            raise ContractError("training label original target/clocks differ from population")
        if population[label.row_id].target_version != fit.target_definition_ref.sha256:
            raise ContractError("population target differs from retained target")
    row_ids = []
    for identity in fit.actual_training_read_manifests:
        if identity not in ancestors or by[identity].kind != "read_manifest":
            raise ContractError("missing actual training read manifest")
        manifest = by[identity].read_manifest
        requests = tuple(b.request for b in manifest.bindings)
        if not requests or len({r.row_id for r in requests}) != 1:
            raise ContractError("training read manifest must name one sample")
        for request in requests:
            if (request.row_id not in fold.training_ids or request.fold_node_id != fit.fold_node_id
                    or request.purpose != "fit_feature"
                    or request.decision_cut != population[request.row_id].decision_at
                    or request.assembled_at > fit.fit_cut):
                raise ContractError("training read outside admitted fit population/cut")
        row_ids.append(requests[0].row_id)
    if set(row_ids) != set(fold.training_ids) or len(row_ids) != len(set(row_ids)):
        raise ContractError("actual training reads incomplete")
    for identity in ancestors - {node.id}:
        upstream = by[identity].fit_evidence
        if upstream and upstream.actual_fit_completion_at > fit.fit_cut:
            raise ContractError("future fitted ancestor")


def validate_oof_producer(request, producer_id, verified_commit):
    closure = _validated_closure(verified_commit)
    return _oof(request, producer_id, closure)


def _oof(request, producer_id, closure):
    if type(request) is not ReadRequest or request.target_definition_ref is None:
        raise ContractError("OOF requires an exact original target request")
    by = closure.by_id
    if request.fold_node_id not in by or by[request.fold_node_id].kind != "fold":
        raise ContractError("OOF request lacks predeclared fold contract")
    contract = by[request.fold_node_id].fold_evidence
    routes = dict(contract.declared_routes)
    population = {s.id: s for s in contract.population}
    sample = population.get(request.row_id)
    evaluation_contract = contract
    if request.purpose == "fit_feature":
        producer = by.get(producer_id)
        producer_fold = producer.fit_evidence.fold_node_id if producer is not None and producer.fit_evidence else None
        if (routes.get(producer_id) != producer_fold or producer_fold not in by
                or request.row_id not in contract.fold.training_ids):
            raise ContractError("downstream training requires explicit exact earlier producer route")
        evaluation_contract = by[producer_fold].fold_evidence
        if evaluation_contract is None or {x.id:x for x in evaluation_contract.population}.get(request.row_id) != sample:
            raise ContractError("downstream training original sample differs")
    if (sample is None or sample.date_group != request.date_group
            or request.row_id not in evaluation_contract.fold.evaluation_ids
            or not evaluation_contract.fold.evaluation_start <= request.decision_cut < evaluation_contract.fold.evaluation_end
            or request.decision_cut != sample.decision_at or request.target_start != sample.decision_at
            or request.target_end != sample_target_end(sample) or request.target_definition_ref.sha256 != sample.target_version):
        raise ContractError("OOF original evaluation sample/group/target/clocks differ")
    visited = []
    for identity in sorted(_ancestors(producer_id, by)):
        node = by[identity]
        if node.kind == "final_prediction":
            raise ContractError("final-fit substitution")
        fit = node.fit_evidence
        if fit is None:
            continue
        expected = routes.get(identity, request.fold_node_id)
        if (fit.fold_node_id != expected or fit.actual_fit_completion_at > request.decision_cut
                or request.row_id in fit.training_sample_ids or request.date_group in fit.training_groups
                or (request.target_definition_ref is not None and fit.target_definition_ref != request.target_definition_ref)):
            raise ContractError("OOF fitted ancestor violates route/exclusion/target/clock")
        visited.append(identity)
    if not visited:
        raise ContractError("OOF producer has no fitted closure")
    return tuple(visited)


def _admit(closure, node_id, column, request):
    if type(request) is not ReadRequest:
        raise ContractError("typed read request required")
    by = closure.by_id
    if node_id not in by:
        raise DependencyUnavailable("node absent from exact committed closure")
    node = by[node_id]
    if node.schema_id != request.schema_id or node.unit != request.unit:
        raise ContractError("schema or unit mismatch")
    row = _row(node, request.row_id, column)
    if request.purpose == "audit":
        return row
    if node.kind == "label" and request.purpose != "fit_label":
        raise ContractError("label unavailable to inference/features")
    if request.purpose == "fit_label" and node.kind != "label":
        raise ContractError("fit label view requires label role")
    if node.kind == "final_prediction" and request.purpose in {"fit_feature", "OOF"}:
        raise ContractError("final prediction cannot substitute OOF")
    if request.purpose in {"fit_feature", "fit_label"}:
        if request.fold_node_id not in by or by[request.fold_node_id].kind != "fold":
            raise ContractError("training read fold absent")
        f = by[request.fold_node_id].fold_evidence
        samples = {s.id: s for s in f.population}
        if request.row_id not in f.fold.training_ids or samples[request.row_id].date_group != request.date_group:
            raise ContractError("training read outside declared membership")
        if request.purpose == "fit_label":
            sample = samples[request.row_id]
            target = next((t for t in node.label_targets if t.row_id == request.row_id), None)
            if (target is None or request.target_definition_ref != target.target_definition_ref
                    or request.target_start != sample.decision_at or request.target_end != sample_target_end(sample)
                    or request.decision_cut != f.fold.fit_at or row.input_known_at != sample.label_known_at):
                raise ContractError("fit-label exact original target/maturity differs")
        if request.purpose == "fit_feature" and request.decision_cut != samples[request.row_id].decision_at:
            raise ContractError("training feature original decision differs")
        if request.assembled_at > f.fold.fit_at:
            raise ContractError("training read after frozen fit cut")
    prediction = node.prediction_evidence
    if prediction:
        if (request.target_definition_ref != prediction.target_definition_ref or request.target_start != prediction.target_start
                or request.target_end != prediction.target_end or prediction.row_id != request.row_id):
            raise ContractError("prediction target/endpoints mismatch")
        if prediction.decision_cut != request.decision_cut or prediction.known_at > request.assembled_at:
            raise DependencyUnavailable("prediction cut/completion unavailable")
        if request.assembled_at >= prediction.target_end:
            raise DependencyUnavailable("original prediction horizon expired")
        if node.kind == "oof_prediction" and request.purpose in {"fit_feature", "OOF"}:
            _oof(request, prediction.fit_root_id, closure)
    elif node.derivations:
        derivation = next(d for d in node.derivations if d.row_id == request.row_id)
        if derivation.decision_cut != request.decision_cut or derivation.actual_completion_at > request.assembled_at:
            raise DependencyUnavailable("derived row cut/completion unavailable")
    elif row.input_known_at > request.decision_cut or row.observed_at > request.decision_cut:
        raise DependencyUnavailable("external input after frozen cut")
    if row.valid_from is not None and request.decision_cut < row.valid_from:
        raise DependencyUnavailable("input validity has not begun")
    if row.valid_until is not None and request.assembled_at >= row.valid_until:
        raise DependencyUnavailable("input validity expired")
    return row


def _validate_read_manifest(node, closure):
    manifest = node.read_manifest
    if manifest.namespace != closure.namespace:
        raise ContractError("read namespace mismatch")
    direct = {d.slot: d for d in node.dependencies}
    for binding in manifest.bindings:
        fold_id=binding.request.fold_node_id
        if fold_id is not None and (fold_id not in closure.by_id or closure.by_id[fold_id].kind!="fold"
                or not any(d.source_id==fold_id for d in node.dependencies)):
            raise ContractError("actual-read typed fold must be directly retained")
    for record in manifest.reads:
        b = record.binding
        dep = direct.get(b.column)
        if (dep is None or dep.source_id != b.node_id or dep.columns != (b.source_column,)
                or dep.use != ("provenance" if b.request.purpose in {"audit", "fit_label"} else "value")):
            raise ContractError("actual read requires exact direct column slot")
        if _admit(closure, b.node_id, b.source_column, b.request) != record.row:
            raise IntegrityError("actual read differs from retained row")


def _validate_prediction(node, closure):
    by = closure.by_id; p = node.prediction_evidence
    ancestors = _ancestors(node.id, by)
    if p.fit_root_id not in ancestors or by[p.fit_root_id].kind not in FITTED:
        raise ContractError("prediction fit closure absent")
    if p.read_manifest_id not in ancestors or by[p.read_manifest_id].kind != "read_manifest":
        raise ContractError("prediction actual reads absent")
    if {d.source_id for d in node.dependencies if by[d.source_id].kind in FITTED} != {p.fit_root_id}:
        raise ContractError("prediction requires its exact direct fitted root")
    if {d.source_id for d in node.dependencies if by[d.source_id].kind == "read_manifest"} != {p.read_manifest_id}:
        raise ContractError("prediction requires its exact direct actual-read manifest")
    if any(by[d.source_id].kind not in FITTED | {"read_manifest","definition"} for d in node.dependencies):
        raise ContractError("prediction bypasses actual inference reads")
    fit = by[p.fit_root_id].fit_evidence
    if fit.actual_fit_completion_at > p.decision_cut or fit.target_definition_ref != p.target_definition_ref:
        raise ContractError("future fitted state or target mismatch")
    reads = by[p.read_manifest_id].read_manifest.reads
    if not reads:
        raise ContractError("prediction lacks actual inputs")
    if max(r.row.input_known_at for r in reads) != p.input_known_at:
        raise ContractError("prediction input clock not derived from actual reads")
    for record in reads:
        request = record.binding.request
        if request.purpose != p.mode or request.row_id != p.row_id or request.decision_cut != p.decision_cut or request.assembled_at > p.actual_completion_at:
            raise ContractError("prediction reads disagree with frozen row/cut/completion")
        if p.mode == "OOF":
            _oof(request, p.fit_root_id, closure)
    for row in node.row_evidence:
        _inherited_validity(row, reads, p.actual_completion_at, p.target_end)
    if any(r.row_id != p.row_id or r.input_known_at != p.input_known_at or r.availability_basis != "derived" for r in node.row_evidence):
        raise ContractError("prediction row clock mismatch")


def _inherited_validity(row, reads, completion, endpoint=None):
    expiries = [r.row.valid_until for r in reads if r.row.valid_until is not None]
    if endpoint is not None: expiries.append(endpoint)
    begins = [r.row.valid_from for r in reads if r.row.valid_from is not None]
    if expiries and (row.valid_until is None or row.valid_until > min(expiries) or completion >= min(expiries)):
        raise ContractError("derived row extends inherited original validity")
    if begins and (row.valid_from is None or row.valid_from < max(begins)):
        raise ContractError("derived row precedes inherited validity")


def _validate_derivations(node, closure):
    by = closure.by_id
    derivations = {d.row_id: d for d in node.derivations}
    if len(derivations) != len(node.derivations) or set(derivations) != {r.row_id for r in node.row_evidence}:
        raise ContractError("exact row derivation coverage required")
    direct_reads = {d.source_id for d in node.dependencies if by[d.source_id].kind == "read_manifest"}
    if direct_reads != {d.read_manifest_id for d in node.derivations}:
        raise ContractError("derived actual read manifests differ from direct evidence")
    if any(by[d.source_id].kind not in {"read_manifest", "definition"} for d in node.dependencies):
        raise ContractError("computed row bypasses sanctioned actual reads")
    for row in node.row_evidence:
        d = derivations[row.row_id]
        reads = by[d.read_manifest_id].read_manifest.reads
        if not reads or row.availability_basis != "derived":
            raise ContractError("derived row requires actual input lineage")
        for r in reads:
            q = r.binding.request
            if (q.purpose != "input" or q.row_id != d.row_id or q.decision_cut != d.decision_cut
                    or q.assembled_at > d.actual_completion_at):
                raise ContractError("derived row input execution differs")
        if row.input_known_at != max(r.row.input_known_at for r in reads) or row.observed_at > d.decision_cut:
            raise ContractError("derived row causal clock mismatch")
        _inherited_validity(row, reads, d.actual_completion_at)


@dataclass(frozen=True, slots=True)
class CommitRef:
    key: str
    namespace: str
    configuration_id: str
    manifest_ref: ArtifactRef

    def __post_init__(self):
        for v in (self.key, self.namespace, self.configuration_id): _text(v)
        if type(self.manifest_ref) is not ArtifactRef or self.manifest_ref.kind != "semantic_manifest":
            raise ContractError("typed semantic manifest reference required")


@dataclass(frozen=True, slots=True)
class VerifiedCommit:
    reference: CommitRef
    closure: ClosureManifest
    manifest_bytes: int
    payload_bytes: int

    def __post_init__(self):
        if type(self.reference) is not CommitRef or type(self.closure) is not ClosureManifest:
            raise ContractError("typed verified commit required")
        _validated_closure(self.closure)
        if self.reference.namespace != self.closure.namespace or any(type(v) is not int or v < 0 for v in (self.manifest_bytes, self.payload_bytes)):
            raise ContractError("verified commit dimensions/namespace differ")


class SemanticArtifactStore:
    __slots__ = ("_root", "_namespace", "_limits", "_configuration", "_blobs", "_manifests", "_io")

    def __init__(self, root, namespace, limits=Limits()):
        _text(namespace)
        object.__setattr__(self, "_io", MappingProxyType({"read_calls":0,"read_bytes":0,"blob_put_calls":0,"manifest_put_calls":0,"pointer_publish_calls":0}))
        if type(limits) is not Limits:
            raise ContractError("typed immutable limits required")
        object.__setattr__(self, "_root", Path(root))
        object.__setattr__(self, "_namespace", namespace)
        object.__setattr__(self, "_limits", limits)
        config = canonical_json({"format": 1, "namespace": namespace, "limits": {f.name: getattr(limits, f.name) for f in fields(limits)}})
        object.__setattr__(self, "_configuration", config)
        object.__setattr__(self, "_blobs", ArtifactStore(self._root / "blobs"))
        object.__setattr__(self, "_manifests", ArtifactStore(self._root / "manifests"))
        path = self._root / "configuration.json"
        if path.exists() and self._read_bounded(path, len(config)) != config:
            raise IntegrityError("semantic store configuration mismatch")
        publish_new(path, config)
        self._check_accounting()

    def __setattr__(self, name, value):
        raise AttributeError("semantic store configuration is immutable")

    def __delattr__(self, name):
        raise AttributeError("semantic store configuration is immutable")

    @property
    def root(self): return self._root
    @property
    def namespace(self): return self._namespace
    @property
    def limits(self): return self._limits
    @property
    def configuration_id(self): return _sha(self._configuration)

    @property
    def io_counts(self): return dict(self._io)

    def _count_io(self, **values):
        object.__setattr__(self, "_io", MappingProxyType({k:v+values.get(k,0) for k,v in self._io.items()}))

    def _read_bounded(self, path, bound):
        try:
            with path.open("rb") as stream:
                if os.fstat(stream.fileno()).st_size > bound:
                    raise IntegrityError("retained bytes exceed declared bound")
                value = stream.read(bound + 1)
                if len(value) > bound:
                    raise IntegrityError("retained bytes grew past bound")
                self._count_io(read_calls=1,read_bytes=len(value))
                return value
        except FileNotFoundError as exc:
            raise DependencyUnavailable("required committed bytes absent") from exc

    def _check_configuration(self):
        if self._read_bounded(self.root / "configuration.json", len(self._configuration)) != self._configuration:
            raise IntegrityError("configuration bytes changed")

    def _pointer(self, key):
        _text(key)
        return self.root / "commits" / (_sha(key.encode("utf-8")) + ".json")

    def _blob_read(self, ref, bound, *, manifest=False):
        if ref.size_bytes > bound:
            raise IntegrityError("declared content size exceeds bound")
        raw = self._read_bounded((self._manifests if manifest else self._blobs).path(ref), ref.size_bytes)
        if len(raw) != ref.size_bytes or _sha(raw) != ref.sha256:
            raise IntegrityError("committed content hash/size mismatch")
        return raw

    @contextmanager
    def _mutation(self):
        if any(operation._store.root.resolve() == self.root.resolve()
               for operation in _ACTIVE_READ_OPERATIONS.get()):
            raise ContractError("cannot mutate a semantic store during its active read operation")
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / "mutation.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                self._check_configuration(); self._check_accounting()
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def storage_accounting(self):
        def entries(directory):
            return tuple(p for p in (self.root / directory).glob("*/*") if p.is_file() and not p.name.startswith(".pending-"))
        blobs, manifests = entries("blobs"), entries("manifests")
        pointers = tuple((self.root / "commits").glob("*.json"))
        audits = tuple((self.root / "failed_attempts").glob("*.json"))
        used = set(); live_payloads = set()
        for p in pointers:
            try:
                v = _json(self._read_bounded(p, self.limits.max_manifest_bytes))
                manifest_ref = ArtifactRef(**v["manifest_ref"])
                used.add(manifest_ref.sha256)
                retained = self._blob_read(manifest_ref, self.limits.max_manifest_bytes, manifest=True)
                _, retained_nodes = _decode(retained)
                live_payloads.update(r.sha256 for n in retained_nodes for r in _references(n))
            except DependencyUnavailable:
                raise
            except (ContractError, KeyError, TypeError) as exc:
                raise IntegrityError("invalid retained pointer during accounting") from exc
        orphan_manifests = tuple(p for p in manifests if p.name not in used)
        def pending_bytes(directory, published):
            inodes={(p.stat().st_dev,p.stat().st_ino) for p in published}
            total=0
            for p in (self.root/directory).rglob(".pending-*"):
                try: info=p.stat()
                except FileNotFoundError: continue
                if (info.st_dev,info.st_ino) not in inodes: total+=info.st_size
            return total
        staged_payloads=pending_bytes("blobs",blobs)
        staged_manifests=pending_bytes("manifests",manifests)
        staged_other=pending_bytes("commits",pointers)+pending_bytes("failed_attempts",audits)
        # Unreferenced content remains charged; it is never silently evicted.
        return {"unique_blob_bytes": sum(p.stat().st_size for p in blobs), "commits": len(pointers),
                "manifest_bytes": sum(p.stat().st_size for p in manifests), "manifests": len(manifests),
                "orphan_manifest_bytes": sum(p.stat().st_size for p in orphan_manifests),
                "orphan_blob_bytes": sum(p.stat().st_size for p in blobs if p.name not in live_payloads),
                "staging_payload_bytes": staged_payloads,
                "staging_manifest_bytes": staged_manifests,
                "pointer_bytes": sum(p.stat().st_size for p in pointers),
                "audit_bytes": sum(p.stat().st_size for p in audits), "audits": len(audits),
                "staging_bytes": staged_payloads+staged_manifests+staged_other,
                "mutation_lock_bytes": (self.root / "mutation.lock").stat().st_size if (self.root / "mutation.lock").exists() else 0,
                "configuration_bytes": len(self._configuration)}

    def _check_accounting(self):
        c = self.storage_accounting()
        if (c["unique_blob_bytes"] + c["staging_payload_bytes"] > self.limits.max_store_blob_bytes
                or c["commits"] > self.limits.max_commits):
            raise ContractError("retained aggregate store bound")
        for directory, pattern, bound in (("manifests","*/*",self.limits.max_manifest_bytes),
                                           ("commits","*.json",self.limits.max_manifest_bytes),
                                           ("failed_attempts","*.json",self.limits.max_manifest_bytes)):
            if any(p.is_file() and p.stat().st_size > bound for p in (self.root/directory).glob(pattern)):
                raise ContractError("retained individual envelope bound")
        return c

    def commit(self, commit_key, roots, staged_nodes, payloads, *, _death_point=None):
        # Snapshot the mapping once; exact bytes and frozen nodes are immutable.
        if not isinstance(payloads, Mapping) or len(payloads)>max(1,self.limits.max_manifest_bytes//16):
            raise ContractError("bounded proposed payload mapping required")
        payloads = MappingProxyType(dict(payloads))
        self._pointer(commit_key)
        with self._mutation():
            return self._commit_locked(commit_key, roots, staged_nodes, payloads, _death_point)

    def _commit_locked(self, commit_key, roots, staged_nodes, payloads, _death_point):
        self._check_configuration()
        closure = validate_closure(roots, staged_nodes, payloads, self.namespace, self.limits)
        raw = _encode((closure.roots, closure.nodes))
        if len(raw) > self.limits.max_manifest_bytes:
            raise ContractError("manifest byte bound")
        ref = payload_ref(raw, "semantic_manifest")
        pointer = canonical_json({"key": commit_key, "namespace": self.namespace, "configuration_id": self.configuration_id,
                                  "manifest_ref": {f.name: getattr(ref, f.name) for f in fields(ref)}})
        path = self._pointer(commit_key)
        if len(pointer) > self.limits.max_manifest_bytes:
            raise ContractError("commit pointer byte bound")
        if path.exists():
            old = self._read_bounded(path, self.limits.max_manifest_bytes)
            if old != pointer:
                raise ContractError("commit key already names different complete content")
            return self.read_commit(commit_key).reference
        counts = self.storage_accounting()
        if counts["commits"] >= self.limits.max_commits:
            raise ContractError("commit count bound")
        required = {r.sha256: (r, payloads[r.sha256]) for n in closure.nodes for r in _references(n)}
        added = sum(len(v) for r, v in required.values() if not self._blobs.path(r).exists())
        if counts["unique_blob_bytes"] + counts["staging_payload_bytes"] + added > self.limits.max_store_blob_bytes:
            raise ContractError("unique retained blob byte bound")
        for r, value in required.values():
            if self._blobs.path(r).exists():
                self._blob_read(r,self.limits.max_node_payload_bytes)
            else:
                self._blobs.put_bytes(value, kind=r.kind)
                self._count_io(blob_put_calls=1)
        if self._manifests.path(ref).exists():
            self._blob_read(ref,self.limits.max_manifest_bytes,manifest=True)
        else:
            self._manifests.put_bytes(raw, kind=ref.kind)
            self._count_io(manifest_put_calls=1)
        if _death_point == "before_pointer":
            os._exit(23)
        publish_new(path, pointer)
        self._count_io(pointer_publish_calls=1)
        if _death_point == "after_pointer":
            os._exit(24)
        return CommitRef(commit_key, self.namespace, self.configuration_id, ref)

    def read_commit(self, commit_key):
        self._check_configuration(); self._check_accounting()
        raw_pointer = self._read_bounded(self._pointer(commit_key), self.limits.max_manifest_bytes)
        try:
            pointer = _json(raw_pointer)
            if set(pointer) != {"key", "namespace", "configuration_id", "manifest_ref"}:
                raise ContractError("pointer fields")
            if pointer["key"] != commit_key or pointer["namespace"] != self.namespace or pointer["configuration_id"] != self.configuration_id:
                raise ContractError("pointer identity")
            ref = ArtifactRef(**pointer["manifest_ref"])
            if ref.kind != "semantic_manifest":
                raise ContractError("manifest kind mismatch")
            raw = self._blob_read(ref, self.limits.max_manifest_bytes, manifest=True)
            roots, nodes = _decode(raw)
            if len(nodes) > self.limits.max_nodes_per_commit:
                raise ContractError("restored node bound")
            payloads = {r.sha256: self._blob_read(r, self.limits.max_node_payload_bytes) for n in nodes for r in _references(n)}
            closure = validate_closure(roots, nodes, payloads, self.namespace, self.limits)
        except DependencyUnavailable:
            raise
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
            raise IntegrityError("invalid committed semantic envelope") from exc
        return VerifiedCommit(CommitRef(commit_key, self.namespace, self.configuration_id, ref), closure,
                              len(raw), sum(len(v) for v in payloads.values()))

    @contextmanager
    def read_operation(self, commit_ref):
        """One immutable commit snapshot for one bounded consuming operation.

        Ordinary reads keep their existing revalidation. An opted-in caller
        shares one verified closure only inside this scope. Cooperating store
        mutations are locked out, and exact retained bytes are checked again
        before any result leaves the scope.
        """
        with (self.root / "mutation.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_SH)
            operation = None
            scope_token = None
            try:
                operation = _VerifiedReadOperation(self, commit_ref, _mint=_READ_OPERATION_MINT)
                scope_token = _ACTIVE_READ_OPERATIONS.set((*_ACTIVE_READ_OPERATIONS.get(), operation))
                yield operation
            finally:
                try:
                    if operation is not None:
                        operation.close()
                finally:
                    if scope_token is not None:
                        _ACTIVE_READ_OPERATIONS.reset(scope_token)
                    fcntl.flock(lock, fcntl.LOCK_UN)

    def resolve(self, commit_ref, node_id, column, request):
        if type(commit_ref) is not CommitRef:
            raise ContractError("exact commit reference required")
        if commit_ref.namespace != self.namespace or commit_ref.configuration_id != self.configuration_id:
            raise ContractError("commit used across namespace/configuration")
        commit = self.read_commit(commit_ref.key)
        if commit.reference != commit_ref:
            raise IntegrityError("commit reference mismatch")
        return _admit(commit.closure, node_id, column, request)


class _VerifiedReadOperation:
    __slots__ = ("_store", "_commit", "_closed")

    def __init__(self, store, commit_ref, *, _mint=None):
        if _mint is not _READ_OPERATION_MINT:
            raise ContractError("read operation must be created by its active store scope")
        if type(store) is not SemanticArtifactStore or type(commit_ref) is not CommitRef:
            raise ContractError("read operation requires an exact semantic store and commit")
        commit = store.read_commit(commit_ref.key)
        if commit.reference != commit_ref:
            raise IntegrityError("read operation commit differs from its retained identity")
        object.__setattr__(self, "_store", store)
        object.__setattr__(self, "_commit", commit)
        object.__setattr__(self, "_closed", False)

    def __setattr__(self, name, value):
        raise AttributeError("read operation identity is immutable")

    def __delattr__(self, name):
        raise AttributeError("read operation identity is immutable")

    def read_commit(self, store, commit_ref):
        if self._closed:
            raise ContractError("read operation is closed")
        if not any(operation is self for operation in _ACTIVE_READ_OPERATIONS.get()):
            raise ContractError("read operation is outside its active store scope")
        if store is not self._store or commit_ref != self._commit.reference:
            raise IntegrityError("read operation used across exact store/commit identities")
        return self._commit

    def close(self):
        object.__setattr__(self, "_closed", True)
        store, commit = self._store, self._commit
        store._check_configuration()
        store._check_accounting()
        reference = commit.reference
        expected_pointer = canonical_json({"key": reference.key, "namespace": reference.namespace,
            "configuration_id": reference.configuration_id,
            "manifest_ref": {f.name: getattr(reference.manifest_ref, f.name) for f in fields(reference.manifest_ref)}})
        if store._read_bounded(store._pointer(reference.key), store.limits.max_manifest_bytes) != expected_pointer:
            raise IntegrityError("read operation commit pointer changed")
        store._blob_read(reference.manifest_ref, store.limits.max_manifest_bytes, manifest=True)
        references = {ref.sha256: ref for node in commit.closure.nodes for ref in _references(node)}
        for identity, ref in references.items():
            if store._blob_read(ref, store.limits.max_node_payload_bytes) != commit.closure._payloads[identity]:
                raise IntegrityError("read operation retained source bytes changed")


def _operation_commit(store, commit_ref, operation):
    if operation is None:
        return store.read_commit(commit_ref.key)
    if type(operation) is not _VerifiedReadOperation:
        raise ContractError("typed store read operation required")
    return operation.read_commit(store, commit_ref)


@dataclass(frozen=True, slots=True)
class _ReadConfiguration:
    store: SemanticArtifactStore
    commit_ref: CommitRef
    bindings: tuple[ReadBinding, ...]
    operation: _VerifiedReadOperation | None = None


class ReadSession:
    __slots__ = ("_configuration", "_reads", "_omissions", "_sealed")

    def __init__(self, store, commit_ref, bindings, *, read_operation=None):
        _tuple(bindings, ReadBinding)
        _names(tuple(b.column for b in bindings))
        _coherent_bindings(bindings)
        if not bindings or type(store) is not SemanticArtifactStore or type(commit_ref) is not CommitRef:
            raise ContractError("typed nonempty read session required")
        if len(bindings) > store.limits.max_columns_per_row:
            raise ContractError("session binding count bound")
        _embedded_bound(bindings, store.limits.max_manifest_bytes)
        if commit_ref.namespace != store.namespace or commit_ref.configuration_id != store.configuration_id:
            raise ContractError("session commit belongs to another store configuration")
        if read_operation is not None:
            _operation_commit(store, commit_ref, read_operation)
        object.__setattr__(self, "_configuration", _ReadConfiguration(store, commit_ref, bindings, read_operation))
        object.__setattr__(self, "_reads", MappingProxyType({}))
        object.__setattr__(self, "_omissions", MappingProxyType({}))
        object.__setattr__(self, "_sealed", None)

    def __setattr__(self, name, value):
        raise AttributeError("actual-read session configuration is immutable")

    def __delattr__(self, name):
        raise AttributeError("actual-read session configuration is immutable")

    @property
    def bindings(self): return self._configuration.bindings

    def _binding(self, column):
        by = {b.column: b for b in self.bindings}
        if column not in by:
            raise ContractError("undeclared actual read")
        if self._sealed is not None:
            raise ContractError("sealed actual-read session")
        return by[column]

    def read(self, column):
        b = self._binding(column)
        if column in self._omissions:
            raise ContractError("input already explicitly omitted")
        c = self._configuration
        row = (c.store.resolve(c.commit_ref, b.node_id, b.source_column, b.request)
               if c.operation is None else _admit(_operation_commit(c.store, c.commit_ref, c.operation).closure,
                                                  b.node_id, b.source_column, b.request))
        record = ReadRecord(b, row)
        if column in self._reads and self._reads[column] != record:
            raise IntegrityError("conflicting repeated actual read")
        object.__setattr__(self, "_reads", MappingProxyType({**self._reads, column: record}))
        return row.value_json

    def omit_optional(self, column, reason):
        b = self._binding(column)
        if b.required or reason not in b.omission_reasons or column in self._reads:
            raise ContractError("invalid optional omission")
        if column in self._omissions and self._omissions[column] != reason:
            raise ContractError("conflicting optional omission")
        object.__setattr__(self, "_omissions", MappingProxyType({**self._omissions, column: reason}))

    def seal(self):
        if self._sealed is not None:
            return self._sealed
        manifest = ReadManifest(self._configuration.store.namespace, self.bindings,
                                tuple(self._reads[b.column] for b in self.bindings if b.column in self._reads),
                                tuple(sorted(self._omissions.items())))
        object.__setattr__(self, "_sealed", manifest)
        return manifest


@dataclass(frozen=True, slots=True)
class RebuildPlan:
    rebuilt_keys: tuple[str, ...]
    reused_keys: tuple[str, ...]
    rebuilt_ids: tuple[str, ...]
    reused_ids: tuple[str, ...]
    first_change_paths: tuple[tuple[str, tuple[str, ...]], ...]


def plan_rebuild(previous_commit, proposed_specs, changed_keys, *, payloads=None, roots=None):
    closure = _validated_closure(previous_commit)
    if payloads is None:
        raise ContractError("proposed rebuild requires retained validation bytes")
    _tuple(proposed_specs,SemanticNodeSpec)
    _admit_node_sizes(proposed_specs,closure._limits)
    proposed_by_key={n.logical_key:n for n in proposed_specs}
    old_root_keys=tuple(closure.by_id[i].logical_key for i in closure.roots)
    if any(k not in proposed_by_key for k in old_root_keys):
        raise ContractError("rebuild root absent from proposed closure")
    expected_roots=tuple(sorted(proposed_by_key[k].id for k in old_root_keys))
    roots=expected_roots if roots is None else roots
    _names(roots)
    if tuple(sorted(roots))!=expected_roots:
        raise ContractError("rebuild changes the declared root set")
    proposed = validate_closure(roots, proposed_specs, payloads, closure.namespace, closure._limits)
    proposed_specs = proposed.nodes
    _tuple(proposed_specs, SemanticNodeSpec); _names(changed_keys)
    old = {n.logical_key: n for n in closure.nodes}
    new = {n.logical_key: n for n in proposed_specs}
    if len(new) != len(proposed_specs) or set(old) != set(new) or not set(changed_keys) <= set(old):
        raise ContractError("rebuild requires the same explicit finite logical graph")
    reverse = {k: set() for k in old}
    old_ids = {n.id: k for k, n in old.items()}
    new_ids = {n.id: k for k, n in new.items()}
    for table, ids in ((old, old_ids), (new, new_ids)):
        for key, n in table.items():
            if n.namespace != closure.namespace:
                raise ContractError("rebuild namespace mismatch")
            for d in n.dependencies:
                if d.source_id not in ids:
                    raise ContractError("missing proposed dependency")
                reverse[ids[d.source_id]].add(key)
    paths = {k: (k,) for k in sorted(changed_keys)}
    todo = list(sorted(changed_keys))
    while todo:
        source = todo.pop(0)
        for consumer in sorted(reverse[source]):
            if consumer not in paths:
                paths[consumer] = (*paths[source], consumer); todo.append(consumer)
    if any(old[k].id != new[k].id for k in old.keys() - paths.keys()):
        raise ContractError("undeclared changed seed outside affected closure")
    rebuilt = tuple(sorted(paths)); reused = tuple(sorted(old.keys() - paths.keys()))
    return RebuildPlan(rebuilt, reused, tuple(new[k].id for k in rebuilt), tuple(new[k].id for k in reused), tuple(sorted(paths.items())))


def attest_state(model, node, payloads, actual_columns, manifest):
    """Exact payload/order equality; serving additionally validates the fitted closure."""
    if node.kind not in FITTED or not is_dataclass(model):
        raise ContractError("typed fitted model state required")
    _names(actual_columns)
    raw = canonical_json(model)
    if payloads.get(node.payload_ref.sha256) != raw or payload_ref(raw).sha256 != node.payload_ref.sha256:
        raise IntegrityError("actual model parameters differ from admitted immutable payload")
    declared = tuple(b.column for b in manifest.bindings)
    read = tuple(r.binding.column for r in manifest.reads)
    if actual_columns != declared or actual_columns != read:
        raise ContractError("actual model column order differs from actual-read manifest")
    return node.id


def _model_domain(model):
    from trading_research.research.models import BinaryModel, FrequencyModel
    from trading_research.research.calibration import CalibratedBinary
    from trading_research.research.scoring import finite, probability
    if type(model) is CalibratedBinary:
        if not 0 < finite(model.probability_floor) < .5:
            raise ContractError("calibration floor outside open probability domain")
        _model_domain(model.base); _model_domain(model.calibration)
        if model.calibration.columns != ("raw_logit",):
            raise ContractError("calibration input must be the retained raw logit")
        return
    if type(model) not in (BinaryModel, FrequencyModel):
        raise ContractError("uninstrumented model class")
    _names(model.columns)
    if not model.columns:
        raise ContractError("empty model columns")
    _text(model.target_version)
    if type(model) is BinaryModel:
        for values in (model.means, model.scales, model.coefficients):
            _tuple(values)
            if len(values) != len(model.columns): raise ContractError("binary dimensions differ")
            for v in values: finite(v)
        if any(v <= 0 for v in model.scales): raise ContractError("nonpositive standardization scale")
        for v in (model.intercept, model.l2_strength, model.maximum_gradient, model.objective): finite(v)
        if model.l2_strength < 0 or model.maximum_gradient < 0 or type(model.iterations) is not int or model.iterations < 0:
            raise ContractError("invalid supplied fit diagnostics")
    else:
        _tuple(model.cuts, tuple); _tuple(model.cells, tuple)
        if len(model.cells)>4096 or any(len(edges)>128 for edges in model.cuts):
            raise ContractError("finite supplied frequency state bound")
        if len(model.cuts) != len(model.columns): raise ContractError("frequency dimensions differ")
        probability(model.overall)
        if finite(model.prior_strength) <= 0 or model.prior_center not in ("uniform", "training_overall"):
            raise ContractError("invalid frequency prior")
        for edges in model.cuts:
            for v in edges: finite(v)
            if tuple(sorted(set(edges))) != edges: raise ContractError("frequency cuts not strictly ordered")
        seen = set()
        for cell in model.cells:
            if len(cell) != 3: raise ContractError("malformed frequency cell")
            key, successes, count = cell
            _tuple(key, int)
            if (len(key) != len(model.columns) or key in seen
                    or any(k < 0 or k > len(e) for k,e in zip(key, model.cuts))
                    or type(successes) is not int or type(count) is not int or count <= 0 or not 0 <= successes <= count):
                raise ContractError("incoherent frequency counts")
            seen.add(key)
        if not model.cells or model.overall != (sum(a for _,a,_ in model.cells)+1)/(sum(b for _,_,b in model.cells)+2):
            raise ContractError("frequency overall differs from complete cell counts")


def training_standardization(verified, node_id, columns):
    """Recompute finite population moments solely from admitted training reads."""
    import math
    from trading_research.research.scoring import finite
    closure=_validated_closure(verified); _names(columns)
    node=closure.by_id.get(node_id)
    if node is None or node.fit_evidence is None:
        raise ContractError("standardization requires retained fitted membership")
    rows=[]
    for identity in node.fit_evidence.actual_training_read_manifests:
        manifest=closure.by_id[identity].read_manifest
        by_column={r.binding.column:r for r in manifest.reads}
        if tuple(b.column for b in manifest.bindings)!=columns or set(by_column)!=set(columns):
            raise ContractError("standardization actual training column order differs")
        rows.append(tuple(finite(_json(by_column[c].row.value_json)) for c in columns))
    if not rows: raise ContractError("empty standardization population")
    means=tuple(math.fsum(r[j] for r in rows)/len(rows) for j in range(len(columns)))
    scales=tuple(math.sqrt(math.fsum((r[j]-means[j])**2 for r in rows)/len(rows)) or 1. for j in range(len(columns)))
    return means,scales


def _attest_components(model, node, closure, payloads):
    from trading_research.research.models import BinaryModel, FrequencyModel
    from trading_research.research.calibration import CalibratedBinary
    from trading_research.research.scoring import finite
    by = closure.by_id
    actual = canonical_json(model)
    if payloads[node.payload_ref.sha256] != actual:
        raise IntegrityError("actual fitted component differs from retained state")
    columns = model.base.columns if type(model) is CalibratedBinary else model.columns
    config = _json(node.execution.configuration_json)
    for identity in node.fit_evidence.actual_training_read_manifests:
        training=by[identity].read_manifest
        if tuple(b.column for b in training.bindings)!=columns:
            raise ContractError("fitted state columns differ from actual training declaration")
    if type(config) is not dict or config.get("input_columns") != list(columns):
        raise ContractError("fitted execution input order differs")
    candidates = [by[i] for i in _ancestors(node.id, by) - {node.id} if by[i].kind in FITTED]
    if type(model) is CalibratedBinary:
        for component in (model.base, model.calibration):
            matches = [n for n in candidates if payloads[n.payload_ref.sha256] == canonical_json(component)]
            if len(matches) != 1:
                raise ContractError("nested fitted component absent or ambiguous")
            _attest_components(component, matches[0], closure, payloads)
    else:
        if model.target_version != node.fit_evidence.target_definition_ref.sha256:
            raise ContractError("actual model target differs from fitted semantic target")
        if type(model) is FrequencyModel:
            labels={r.row_id:r for r in node.fit_evidence.training_label_refs}
            cells={}
            for identity in node.fit_evidence.actual_training_read_manifests:
                manifest=by[identity].read_manifest
                values=tuple(finite(_json(r.row.value_json)) for r in manifest.reads)
                key=tuple(sum(v>=edge for edge in edges) for v,edges in zip(values,model.cuts))
                label=labels[manifest.reads[0].row.row_id]
                outcome=_json(_row(by[label.label_node_id],label.row_id,label.column).value_json)
                if type(outcome) is not int or outcome not in (0,1): raise ContractError("frequency fit requires exact binary labels")
                success,count=cells.get(key,(0,0));cells[key]=(success+outcome,count+1)
            if tuple(sorted((k,a,b) for k,(a,b) in cells.items()))!=tuple(sorted(model.cells)):
                raise ContractError("frequency supplied cells differ from actual training population")
        if type(model) is BinaryModel:
            if training_standardization(closure,node.id,model.columns) != (model.means,model.scales):
                raise ContractError("actual standardization differs from admitted training population")
            standardization = canonical_json({"means": model.means, "scales": model.scales})
            refs = dict(node.execution.transform_state_refs)
            ref = refs.get("standardization")
            if (ref is None or payloads.get(ref.sha256) != standardization
                    or not any(n.kind == "transform" and n.payload_ref == ref for n in candidates)):
                raise ContractError("actual standardization lacks exact fitted ancestor")


def serve_bound_model(model, store, commit_ref, node_id, session):
    """Sanctioned finite supplied-state adapter; no fitting or model search."""
    from trading_research.research.models import BinaryModel, FrequencyModel, sigmoid
    from trading_research.research.calibration import CalibratedBinary
    from trading_research.research.scoring import finite, probability
    import math
    if type(store) is not SemanticArtifactStore or type(commit_ref) is not CommitRef or type(session) is not ReadSession:
        raise ContractError("typed committed serving boundary required")
    configuration = session._configuration
    if configuration.store is not store or configuration.commit_ref != commit_ref:
        raise ContractError("served session belongs to another exact commit/store")
    _model_domain(model)
    commit = _operation_commit(store, commit_ref, configuration.operation)
    if commit.reference != commit_ref or node_id not in commit.closure.by_id:
        raise IntegrityError("served model not in named complete commit")
    node = commit.closure.by_id[node_id]
    if node.kind not in FITTED:
        raise ContractError("served node is not fitted state")
    columns = model.base.columns if type(model) is CalibratedBinary else model.columns
    _attest_components(model, node, commit.closure, commit.closure._payloads)
    request = session.bindings[0].request
    if request.purpose not in {"OOF", "final"} or request.target_definition_ref is None:
        raise ContractError("serving requires coherent OOF or final target request")
    if request.purpose == "OOF":
        validate_oof_producer(request, node_id, commit)
    else:
        if request.target_start != request.decision_cut or request.assembled_at >= request.target_end:
            raise ContractError("final serving original target expired or shifted")
        for i in _ancestors(node_id, commit.closure.by_id):
            fit = commit.closure.by_id[i].fit_evidence
            if fit and (fit.actual_fit_completion_at > request.decision_cut or fit.target_definition_ref != request.target_definition_ref):
                raise ContractError("final fitted ancestor target/completion differs")
    values = tuple(finite(_json(session.read(c))) for c in columns)
    manifest = session.seal()
    attest_state(model, node, commit.closure._payloads, columns, manifest)
    for record in manifest.reads:
        b = record.binding
        if _admit(commit.closure, b.node_id, b.source_column, b.request) != record.row:
            raise IntegrityError("served actual read differs from admitted commit")
    def calculate(candidate, x):
        if type(candidate) is BinaryModel:
            return sigmoid(candidate.intercept + math.fsum(w*(v-m)/s for w,v,m,s in zip(candidate.coefficients,x,candidate.means,candidate.scales)))
        if type(candidate) is FrequencyModel:
            key = tuple(sum(v >= c for c in edges) for v, edges in zip(x, candidate.cuts))
            cell = next(((s,n) for k,s,n in candidate.cells if k == key), None)
            center = .5 if candidate.prior_center == "uniform" else candidate.overall
            return candidate.overall if cell is None else (cell[0]+candidate.prior_strength*center)/(cell[1]+candidate.prior_strength)
        p = calculate(candidate.base, x)
        p = min(1-candidate.probability_floor, max(candidate.probability_floor, p))
        return calculate(candidate.calibration, (math.log(p)-math.log1p(-p),))
    return probability(calculate(model, values)), manifest


def restore_bound_model(store, commit_ref, node_id, *, read_operation=None):
    """Reconstruct only the three admitted supplied-state schemas from a commit."""
    from trading_research.research.models import BinaryModel, FrequencyModel
    from trading_research.research.calibration import CalibratedBinary
    from trading_research.research.folds import FittedArtifact
    commit=_operation_commit(store, commit_ref, read_operation)
    if commit.reference != commit_ref or node_id not in commit.closure.by_id:
        raise IntegrityError("restored model exact commit differs")
    node=commit.closure.by_id[node_id]
    def fitted(v):
        if type(v) is not dict or set(v) != {f.name for f in fields(FittedArtifact)}:
            raise ContractError("unknown retained fitted metadata")
        return FittedArtifact(**{**v,"training_ids":frozenset(v["training_ids"]),
                                  "training_groups":frozenset(v["training_groups"]),"upstream_ids":tuple(v["upstream_ids"])})
    def model(v):
        if type(v) is not dict: raise ContractError("unknown supplied model envelope")
        if set(v)=={f.name for f in fields(BinaryModel)}:
            v={**v,"fit_artifacts":tuple(fitted(x) for x in v["fit_artifacts"])}
            for k in ("columns","means","scales","coefficients"): v[k]=tuple(v[k])
            return BinaryModel(**v)
        if set(v)=={f.name for f in fields(FrequencyModel)}:
            return FrequencyModel(**{**v,"columns":tuple(v["columns"]),"cuts":tuple(tuple(x) for x in v["cuts"]),
                "cells":tuple((tuple(k),a,b) for k,a,b in v["cells"]),"artifact":fitted(v["artifact"])})
        if set(v)=={f.name for f in fields(CalibratedBinary)}:
            return CalibratedBinary(**{**v,"base":model(v["base"]),"calibration":model(v["calibration"]),
                "artifact":fitted(v["artifact"]),"upstream":tuple(fitted(x) for x in v["upstream"])})
        raise ContractError("uninstrumented supplied model envelope")
    restored=model(_json(commit.closure._payloads[node.payload_ref.sha256]))
    _model_domain(restored); _attest_components(restored,node,commit.closure,commit.closure._payloads)
    return restored


def numerical_decision(a, b, threshold, tolerance):
    """Exact declared engineering comparison including the downstream decision."""
    from fractions import Fraction
    for value in (a, b, threshold, tolerance):
        if type(value) is not Fraction: raise ContractError("exact rational comparison required")
    if tolerance < 0: raise ContractError("negative tolerance")
    return {"difference": abs(a-b), "within": abs(a-b) <= tolerance,
            "decisions": (a >= threshold, b >= threshold)}


def snapshot_pair(old, new, *, observed_pairing=False):
    """Provenance-only EXT-031 gate; never infer flow or an unobserved pairing."""
    if type(old) is not RowEvidence or type(new) is not RowEvidence or type(observed_pairing) is not bool:
        raise ContractError("typed snapshot evidence required")
    if not observed_pairing or old.acquisition_id == new.acquisition_id or new.observed_at <= old.observed_at:
        raise ContractError("keepalive/reconnect is not a new observed paired snapshot")
    return old.acquisition_id, new.acquisition_id


def evaluate_toy(nodes, roots, *, previous_values=None, affected=None):
    """Registered rational engineering graph, never a learned predictor."""
    from fractions import Fraction
    if len(nodes) > 256 or sum("dependency" in n for n in nodes.values()) > 1024:
        raise ContractError("toy graph bound")
    _names(roots)
    values = {} if previous_values is None else dict(previous_values)
    required = set(nodes) if affected is None else set(affected)
    visiting, visited = set(), set()
    work = {"source_reads": 0, "multiply": 0, "add": 0, "validated_nodes": 0, "validated_edges": 0}
    def run(key):
        if key in visiting or key not in nodes:
            raise ContractError("invalid toy graph")
        if key in visited:
            return values[key]
        visiting.add(key)
        n = nodes[key]; work["validated_nodes"] += 1
        dependency = None
        if "dependency" in n:
            work["validated_edges"] += 1
            dependency = run(n["dependency"])
        if key in required:
            if n["op"] == "source":
                values[key] = Fraction(*n["value"]); work["source_reads"] += 1
            elif n["op"] in {"multiply", "add"} and dependency is not None:
                constant = Fraction(*n["constant"])
                values[key] = dependency * constant if n["op"] == "multiply" else dependency + constant
                work[n["op"]] += 1
            else:
                raise ContractError("unknown toy operation")
        elif key not in values:
            raise ContractError("missing reusable toy state")
        visiting.remove(key); visited.add(key)
        return values[key]
    for root in roots:
        run(root)
    if visited != set(nodes):
        raise ContractError("extra unreachable toy nodes")
    return values, work


def record_failed_attempt(store, *, registry, trial_id, attempt_id, status, reserved_cpu_seconds, partial_refs=()):
    """Retain failed evidence only after reconciliation to the real trial ledger."""
    from dataclasses import asdict
    from trading_research.operations.trials import TrialRegistry
    if type(store) is not SemanticArtifactStore or type(registry) is not TrialRegistry:
        raise ContractError("typed semantic store and trial registry required")
    _text(trial_id); _text(attempt_id); _tuple(partial_refs, ArtifactRef)
    if type(status) is not str or status not in {"failed", "interrupted"} or type(reserved_cpu_seconds) is not int:
        raise ContractError("failed/interrupted attempt evidence required")
    state = registry.state()
    attempt = state["attempts"].get(attempt_id)
    if (trial_id not in state["trials"] or attempt is None or attempt["trial_id"] != trial_id
            or attempt["status"] != status or attempt["cpu_reservation_seconds"] != reserved_cpu_seconds):
        raise ContractError("attempt audit differs from retained registry outcome")
    for ref in partial_refs:
        registry.artifacts.read(ref)
        if asdict(ref) not in attempt["result_artifacts"]:
            raise ContractError("partial artifact not retained on the actual attempt")
    raw = canonical_json({"trial_id": trial_id, "attempt_id": attempt_id, "status": status,
                          "reserved_cpu_seconds": reserved_cpu_seconds, "partial_refs": partial_refs,
                          "cpu_seconds": attempt["cpu_seconds"], "resource_basis": attempt["resource_basis"]})
    path = store.root / "failed_attempts" / (_sha(attempt_id.encode()) + ".json")
    with store._mutation():
        counts = store.storage_accounting()
        if len(raw) > store.limits.max_manifest_bytes:
            raise ContractError("failed audit retained bound")
        publish_new(path, raw)
    return payload_ref(raw, "failed_attempt_audit")
