"""Retain and serve the finite E0 binary fits through the actual F11 store.

The input port retains the caller's published InputValue snapshots verbatim.
It does not assert exchange receipts or turn unavailable/fitted inputs into raw
sources. Calibration logits are separate OOF prediction rows produced by an
actual committed base-model read, never declared as external source values.
"""

from dataclasses import dataclass, InitVar
from fractions import Fraction
from types import MappingProxyType
import json
import math
import platform
from typing import Mapping

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import ArtifactRef, canonical_json, digest
from trading_research.operations.artifact_graph import (
    CommitRef, DependencyRef, ExecutionIdentity, FitEvidence, LabelEvidence,
    LabelTarget, PredictionEvidence, ReadBinding, ReadManifest, ReadRequest,
    ReadSession, RowEvidence, SemanticArtifactStore, SemanticNodeSpec,
    ValidatedFoldEvidence, payload_ref, restore_bound_model, sample_target_end,
    serve_bound_model, validate_oof_producer,
)
from trading_research.research.calibration import CalibratedBinary
from trading_research.research.folds import FittedArtifact, Fold, Sample
from trading_research.research.models import (
    BinaryExample, BinaryModel, FrequencyModel, preflight_training,
)


SCHEMA = "E0BinaryInputs.v1"
UNIT = "declared_numeric_feature"

_HEAD_RECEIPT_MINT = object()


@dataclass(frozen=True, slots=True)
class E0VerifiedHeadReceipt:
    """Immutable output minted from one actual retained serving operation."""

    commit_ref: CommitRef
    model_id: str
    model_node_id: str
    request: ReadRequest
    manifest: ReadManifest
    fitted_nodes: tuple[tuple[str, FitEvidence], ...]
    probability: Fraction
    fold_version: str
    source_node_id: str
    _mint: InitVar[object] = None

    def __post_init__(self, _mint):
        if _mint is not _HEAD_RECEIPT_MINT:
            raise ContractError("verified head receipts require an actual store serving operation")
        if (type(self.commit_ref) is not CommitRef or type(self.request) is not ReadRequest
                or type(self.manifest) is not ReadManifest or not self.manifest.reads
                or self.manifest.namespace != self.commit_ref.namespace
                or self.request.purpose != "OOF"
                or any(binding.request != self.request or binding.node_id != self.source_node_id
                       for binding in self.manifest.bindings)
                or type(self.fitted_nodes) is not tuple or not self.fitted_nodes
                or any(type(fit) is not FitEvidence for _, fit in self.fitted_nodes)
                or self.model_node_id not in dict(self.fitted_nodes)
                or type(self.probability) is not Fraction or not 0 <= self.probability <= 1):
            raise ContractError("verified head receipt differs from actual typed serving evidence")

    @property
    def fitted_at(self):
        return max(fit.actual_fit_completion_at for _, fit in self.fitted_nodes)


def _columns(model):
    return model.base.columns if type(model) is CalibratedBinary else model.columns


def _request(sample, target_ref, fold_node_id, purpose="OOF"):
    return ReadRequest(sample.id, sample.decision_at, sample.decision_at,
        purpose, SCHEMA, UNIT, target_ref, sample.decision_at,
        sample_target_end(sample), sample.date_group, fold_node_id)


def _fit_artifacts(model):
    if type(model) is FrequencyModel:
        return (model.artifact,)
    if type(model) in (BinaryModel, CalibratedBinary):
        return model.fit_artifacts
    raise ContractError("E0 retained serving supports exact binary/frequency/calibrated models")


def _local_artifact(model):
    return model.fit_artifacts[-1] if type(model) is BinaryModel else model.artifact


@dataclass(frozen=True)
class E0ModelBinding:
    store: SemanticArtifactStore
    commit_ref: CommitRef
    model_node_id: str
    source_node_id: str
    fold_node_id: str
    target_ref: ArtifactRef
    model_id: str

    @property
    def node_id(self):
        return self.model_node_id

    def reopen(self, *, read_operation=None):
        if read_operation is None:
            with self.store.read_operation(self.commit_ref) as operation:
                return self.reopen(read_operation=operation)
        model = restore_bound_model(self.store, self.commit_ref, self.model_node_id,
                                    read_operation=read_operation)
        if model.id != self.model_id:
            raise IntegrityError("E0 reopened model identity differs from its binding")
        verified = read_operation.read_commit(self.store, self.commit_ref)
        if verified.reference != self.commit_ref:
            raise IntegrityError("E0 reopened commit identity differs from its binding")
        by = verified.closure.by_id
        def check_component(component, node):
            evidence = by[node.fit_evidence.fold_node_id].fold_evidence
            _validate_fitted_metadata(component, evidence.fold, evidence.population, self.target_ref)
            if type(component) is CalibratedBinary:
                matches = tuple(candidate for candidate in by.values()
                    if candidate.fit_evidence is not None
                    and verified.closure._payloads[candidate.payload_ref.sha256] == canonical_json(component.base))
                if len(matches) != 1:
                    raise IntegrityError("E0 reopened calibration lacks one exact earlier base")
                check_component(component.base, matches[0])
        check_component(model, by[self.model_node_id])
        return model

    def predict(self, example, *, supplied_model=None):
        """Reopen the model and resolve the original row through a real session."""
        if type(example) is not BinaryExample:
            raise ContractError("E0 committed query requires an exact BinaryExample")
        example.__post_init__()
        with self.store.read_operation(self.commit_ref) as operation:
            return self._predict_in_operation(example, operation, supplied_model)

    def _predict_in_operation(self, example, operation, supplied_model):
        model = self.reopen(read_operation=operation)
        if supplied_model is not None and (supplied_model.id != self.model_id
                or canonical_json(supplied_model) != canonical_json(model)):
            raise IntegrityError("E0 supplied query model differs from its actual retained state")
        verified = operation.read_commit(self.store, self.commit_ref)
        if verified.reference != self.commit_ref:
            raise IntegrityError("E0 query commit changed")
        evidence = verified.closure.by_id[self.fold_node_id].fold_evidence
        if {s.id: s for s in evidence.population}.get(example.sample.id) != example.sample:
            raise IntegrityError("E0 query sample differs from its complete retained population")
        source = verified.closure.by_id[self.source_node_id]
        retained = {(r.row_id, r.column): r for r in source.row_evidence}
        supplied = {v.column: v for v in example.values}
        columns = _columns(model)
        for column in columns:
            value = supplied.get(column)
            row = retained.get((example.sample.id, column))
            if (value is None or row is None or value.unavailable_reason is not None
                    or value.fitted_dependency_ids or value.fold_version is not None
                    or (value.version, value.known_at, value.payload_json) !=
                       (row.source_version, row.input_known_at, row.value_json)):
                raise IntegrityError("E0 query differs from the actual retained published input")
        request = _request(example.sample, self.target_ref, self.fold_node_id)
        session = ReadSession(self.store, self.commit_ref, tuple(
            ReadBinding(column, self.source_node_id, column, request) for column in columns),
            read_operation=operation)
        probability, manifest = serve_bound_model(model, self.store, self.commit_ref,
                                                  self.model_node_id, session)
        closure = validate_oof_producer(request, self.model_node_id, verified)
        receipt = E0VerifiedHeadReceipt(self.commit_ref, model.id, self.model_node_id,
            request, manifest, tuple((node_id, verified.closure.by_id[node_id].fit_evidence)
                                     for node_id in closure), Fraction(str(probability)),
            evidence.fold.version,
            self.source_node_id,
            _mint=_HEAD_RECEIPT_MINT)
        return probability, MappingProxyType({
            "commit_ref": self.commit_ref,
            "model_node_id": self.model_node_id,
            "source_node_id": self.source_node_id,
            "fold_node_id": self.fold_node_id,
            "actual_target_definition": verified.closure._payloads[self.target_ref.sha256],
            "request": request,
            "actual_read_manifest": manifest,
            "fitted_closure": closure,
            "verified_head_receipt": receipt,
        })

    def __call__(self, model, example):
        return self.predict(example, supplied_model=model)


@dataclass(frozen=True)
class E0CommittedBinaryFit:
    bindings: tuple[E0ModelBinding, ...]
    fit_version: str

    def binding(self, model):
        matches = tuple(b for b in self.bindings if b.model_id == model.id)
        if len(matches) != 1:
            raise ContractError("E0 model lacks one exact retained serving binding")
        return matches[0]

    def __call__(self, model, example):
        return self.binding(model)(model, example)


class _Graph:
    def __init__(self, store, namespace, code_ref, target_ref, definition_ref, payloads, upstream):
        if type(store) is not SemanticArtifactStore or namespace != store.namespace:
            raise ContractError("E0 binding requires one exact semantic store namespace")
        if not isinstance(payloads, Mapping):
            raise ContractError("E0 binding requires retained content bytes")
        self.store, self.namespace = store, namespace
        self.code_ref, self.target_ref, self.definition_ref = code_ref, target_ref, definition_ref
        self.payloads = dict(payloads)
        self.nodes = {}
        for binding in upstream:
            if (type(binding) is not E0ModelBinding or binding.store is not store
                    or binding.target_ref != target_ref):
                raise ContractError("E0 upstream binding changes store or target")
            binding.reopen()
            verified = store.read_commit(binding.commit_ref.key)
            if verified.reference != binding.commit_ref:
                raise IntegrityError("E0 upstream commit changed")
            for node in verified.closure.nodes:
                self.add(node)
            for identity, raw in verified.closure._payloads.items():
                if identity in self.payloads and self.payloads[identity] != raw:
                    raise IntegrityError("E0 retained upstream payload changed")
                self.payloads[identity] = raw
        for ref in (code_ref, target_ref, definition_ref):
            if type(ref) is not ArtifactRef:
                raise ContractError("E0 code/target/definition must be actual retained references")
            raw = self.payloads.get(ref.sha256)
            if (type(raw) is not bytes or len(raw) != ref.size_bytes
                    or payload_ref(raw).sha256 != ref.sha256):
                raise IntegrityError("E0 code/target/definition bytes differ from their references")
        self.numerical = canonical_json({
            "backend_id": "trading_research.research.models.python_reference_v1",
            "precision": "python_float_binary64",
            "rounding": "IEEE754_round_to_nearest",
            "seed": None,
            "thread_count": 1,
            "library_versions": {"python": platform.python_version()},
        })

    def keep(self, raw, kind="semantic_payload"):
        ref = payload_ref(raw, kind)
        old = self.payloads.get(ref.sha256)
        if old is not None and old != raw:
            raise IntegrityError("E0 semantic payload identity collision")
        self.payloads[ref.sha256] = raw
        return ref

    def add(self, node):
        old = self.nodes.get(node.id)
        if old is not None and old != node:
            raise IntegrityError("E0 semantic node identity collision")
        if any(n.logical_key == node.logical_key and n.id != node.id for n in self.nodes.values()):
            raise IntegrityError("E0 semantic logical identity changed")
        self.nodes[node.id] = node
        return node

    def execution(self, configuration, transforms=()):
        return ExecutionIdentity(self.code_ref, canonical_json(configuration), self.numerical, transforms)

    def node(self, key, kind, *, rows=(), raw=None, dependencies=(), execution=None, **evidence):
        rows = tuple(sorted(rows, key=lambda r: (r.row_id, r.column)))
        if rows:
            raw = canonical_json([[r.row_id, r.column, json.loads(r.value_json)] for r in rows])
        if raw is None:
            raw = canonical_json({"role": key})
        if execution is None and kind not in ("source", "label", "fold", "definition"):
            execution = self.execution({"role": key})
        return self.add(SemanticNodeSpec(self.namespace, key, kind, SCHEMA, UNIT,
            self.definition_ref, self.keep(raw), execution, tuple(dependencies), rows, **evidence))

    def commit(self, key, roots):
        """Publish exactly the reachable closure; no orphan staging nodes."""
        required, pending = set(), list(roots)
        while pending:
            identity = pending.pop()
            if identity in required:
                continue
            node = self.nodes.get(identity)
            if node is None:
                raise ContractError("E0 semantic graph lacks an actual retained dependency")
            required.add(identity)
            pending.extend(d.source_id for d in node.dependencies)
        nodes = tuple(self.nodes[i] for i in sorted(required))
        return self.store.commit(key, tuple(roots), nodes, self.payloads)

    def manifest_node(self, manifest):
        if type(manifest) is not ReadManifest:
            raise ContractError("E0 training requires a real sealed ReadSession manifest")
        dependencies = tuple(DependencyRef(b.column, b.node_id, "value", (b.source_column,))
                             for b in manifest.bindings)
        fold_ids = {b.request.fold_node_id for b in manifest.bindings}
        if len(fold_ids) != 1 or None in fold_ids:
            raise ContractError("E0 actual reads need one exact fold route")
        # The reserved slot does not collide with registered feature columns.
        dependencies += (DependencyRef("__e0_fold__", next(iter(fold_ids)), "provenance"),)
        return self.node("e0:reads:" + manifest.id, "read_manifest",
                         read_manifest=manifest, dependencies=dependencies)


def _source(graph, examples, columns):
    rows = []
    for example in examples:
        values = {v.column: v for v in example.values}
        for column in columns:
            value = values.get(column)
            if value is None or value.unavailable_reason is not None:
                raise DependencyUnavailable("E0 declared model input is unavailable")
            if value.fitted_dependency_ids or value.fold_version is not None:
                raise ContractError("E0 external input port cannot hide fitted input ancestry")
            if value.known_at > example.sample.decision_at:
                raise DependencyUnavailable("E0 input was not published at its original row cut")
            # Existing publication identity is retained; this is not a newly
            # asserted exchange receipt or an inferred earlier event clock.
            rows.append(RowEvidence(example.sample.id, column, value.version, value.version,
                value.known_at, value.known_at, "published", value.payload_json))
    rows = tuple(rows)
    return graph.node("e0:published-inputs:" + digest(rows), "source", rows=rows)


def _labels(graph, examples, fold):
    by = {e.sample.id: e for e in examples}
    rows, targets = [], []
    for identity in fold.training_ids:
        example = by[identity]
        sample = example.sample
        end = sample_target_end(sample)
        rows.append(RowEvidence(identity, "label", digest((sample, example.outcome)),
            sample.target_version + ":" + identity, end, sample.label_known_at,
            "published", canonical_json(example.outcome)))
        targets.append(LabelTarget(identity, graph.target_ref, sample.decision_at, end))
    return graph.node("e0:labels:" + digest((tuple(rows), tuple(targets))), "label",
                      rows=tuple(rows), label_targets=tuple(targets))


def _training_reads(graph, commit, sources, fold_node, examples, columns):
    by = {e.sample.id: e for e in examples}
    manifests = []
    with graph.store.read_operation(commit) as operation:
        for identity in fold_node.fold_evidence.fold.training_ids:
            sample = by[identity].sample
            request = _request(sample, graph.target_ref, fold_node.id, "fit_feature")
            source = sources[identity] if isinstance(sources, dict) else sources
            session = ReadSession(graph.store, commit, tuple(
                ReadBinding(column, source.id, column, request) for column in columns),
                read_operation=operation)
            for column in columns:
                session.read(column)
            manifests.append(graph.manifest_node(session.seal()))
    return tuple(manifests)


def _fit_evidence(graph, fold_node, labels, manifests, examples):
    fold = fold_node.fold_evidence.fold
    by = {e.sample.id: e for e in examples}
    return FitEvidence(fold_node.id, fold.fit_at, fold.fit_at, fold.training_ids,
        tuple(sorted({by[i].sample.date_group for i in fold.training_ids})),
        tuple(LabelEvidence(i, labels.id, "label", graph.target_ref) for i in fold.training_ids),
        tuple(node.id for node in manifests), graph.target_ref)


def _fit_dependencies(fold_node, labels, manifests, upstream=()):
    return (DependencyRef("fold", fold_node.id, "provenance"),
            DependencyRef("labels", labels.id, "fit_label", ("label",)),
            *(DependencyRef("reads:" + str(i), node.id, "provenance") for i, node in enumerate(manifests)),
            *(DependencyRef("fitted:" + str(i), node.id, "provenance") for i, node in enumerate(upstream)))


def _simple_model(graph, model, fold_node, labels, manifests, examples):
    fit = _fit_evidence(graph, fold_node, labels, manifests, examples)
    dependencies = _fit_dependencies(fold_node, labels, manifests)
    config = {"input_columns": model.columns, "model_id": model.id,
              "research_scope": getattr(model, "_research_scope", None)}
    transforms = ()
    if type(model) is BinaryModel:
        state = canonical_json({"means": model.means, "scales": model.scales})
        scaler = graph.node("e0:scaler:" + model.id, "transform", raw=state,
            fit_evidence=fit, dependencies=dependencies,
            execution=graph.execution({"input_columns": model.columns,
                                       "role": "actual_training_standardization"}))
        dependencies += (DependencyRef("standardization", scaler.id, "provenance"),)
        transforms = (("standardization", scaler.payload_ref),)
    return graph.node("e0:model:" + model.id, "model", raw=canonical_json(model),
        fit_evidence=fit, dependencies=dependencies, execution=graph.execution(config, transforms))


def _validate_model_fold(model, fold, examples, target_ref):
    """Do not replace a supplied stale/future fitted declaration with fresh evidence."""
    if type(model) not in (BinaryModel, FrequencyModel, CalibratedBinary):
        raise ContractError("E0 binding requires an exact fitted binary model")
    preflight_training(examples, fold)
    _validate_fitted_metadata(model, fold, tuple(e.sample for e in examples), target_ref)


def _validate_fitted_metadata(model, fold, population, target_ref):
    by = {sample.id: sample for sample in population}
    expected_ids = frozenset(fold.training_ids)
    expected_groups = frozenset(by[i].date_group for i in fold.training_ids)
    expected_known = max(by[i].label_known_at for i in fold.training_ids)
    if any(sample.target_version != target_ref.sha256 for sample in population):
        raise IntegrityError("E0 binary target differs from actual retained target bytes")

    def validate_artifact(artifact):
        if type(artifact) is not FittedArtifact:
            raise ContractError("E0 supplied fitted artifact must be exact and typed")
        artifact.__post_init__()
        if (artifact.fold_version != fold.version or artifact.fitted_at != fold.fit_at
                or artifact.training_ids != expected_ids or artifact.training_groups != expected_groups
                or artifact.training_labels_known_through != expected_known):
            raise IntegrityError("E0 supplied fit metadata differs from the actual complete fold")

    def validate_binary(component):
        if type(component) is not BinaryModel or type(component.fit_artifacts) is not tuple \
                or len(component.fit_artifacts) != 2:
            raise ContractError("E0 binary fit needs its exact local scaler and learner")
        scaler, learner = component.fit_artifacts
        for artifact in (scaler, learner):
            validate_artifact(artifact)
        if (component.target_version != target_ref.sha256 or learner.id != component.id
                or scaler.id == learner.id or scaler.role != "scaler" or learner.role != "binary_logistic"
                or scaler.upstream_ids != () or learner.upstream_ids != (scaler.id,)):
            raise IntegrityError("E0 scaler/learner identities or actual local dependency closure differ")

    if type(model) is BinaryModel:
        validate_binary(model)
    elif type(model) is FrequencyModel:
        validate_artifact(model.artifact)
        if (model.target_version != target_ref.sha256 or model.artifact.id != model.id
                or model.artifact.role != "conditional_frequency" or model.artifact.upstream_ids != ()):
            raise IntegrityError("E0 frequency identity or actual fitted dependency closure differs")
    else:
        validate_artifact(model.artifact)
        validate_binary(model.calibration)
        if (model.artifact.id != model.id or model.artifact.role != "calibrated_binary"
                or model.artifact.upstream_ids != (model.base.id, model.calibration.id)
                or model.upstream != () or not 0 < model.probability_floor < .5):
            raise IntegrityError("E0 calibration omits or changes an actual fitted component")
        # The base belongs to its earlier fold. Its own binding revalidates that
        # complete supplied local artifact closure rather than assigning this
        # calibration fold to it.


def commit_e0_binary(store, *, namespace, code_ref, target_ref, definition_ref,
                     payloads, examples, fold, model, upstream_bindings=()):
    """Commit one supplied fit with authentic training and query read evidence.

    A calibrated model requires its previously committed base binding. Its base
    fold must already include calibration rows in the declared OOF population.
    The helper does not extend a fold, change a target, or refit any model.
    """
    if type(fold) is not Fold or type(upstream_bindings) is not tuple:
        raise ContractError("E0 binding requires a typed fold and immutable upstream bindings")
    examples = tuple(examples)
    if any(type(e) is not BinaryExample or type(e.sample) is not Sample for e in examples):
        raise ContractError("E0 binding requires complete exact binary sample rows")
    if type(target_ref) is not ArtifactRef:
        raise ContractError("E0 binding requires the exact retained target reference")
    _validate_model_fold(model, fold, examples, target_ref)
    if type(model) is not CalibratedBinary and upstream_bindings:
        raise ContractError("unregistered upstream dependency on a standalone E0 binary fit")
    graph = _Graph(store, namespace, code_ref, target_ref, definition_ref, payloads, upstream_bindings)
    population = tuple(sorted((e.sample for e in examples), key=lambda s: (s.decision_at, s.id)))
    prefix = "e0:" + model.id
    routes = tuple(sorted((node.id, node.fit_evidence.fold_node_id)
        for node in graph.nodes.values() if node.fit_evidence is not None))
    fold_node = graph.node(prefix + ":fold", "fold",
        fold_evidence=ValidatedFoldEvidence(population, fold, routes))
    source = _source(graph, examples, _columns(model))
    labels = _labels(graph, examples, fold)
    upstream_roots = tuple(binding.model_node_id for binding in upstream_bindings)
    inputs = graph.commit(prefix + ":inputs", (source.id, labels.id, fold_node.id, *upstream_roots))
    raw_manifests = _training_reads(graph, inputs, source, fold_node, examples, _columns(model))
    if type(model) is not CalibratedBinary:
        fitted_node = _simple_model(graph, model, fold_node, labels, raw_manifests, examples)
    else:
        matches = tuple(b for b in upstream_bindings if b.model_id == model.base.id)
        if len(matches) != 1 or len(upstream_bindings) != 1 or model.upstream:
            raise ContractError("E0 sigmoid binding requires exactly its independently fitted base")
        base = matches[0]
        if canonical_json(base.reopen()) != canonical_json(model.base):
            raise IntegrityError("E0 sigmoid base differs from actual committed state")
        logits = {}
        by = {e.sample.id: e for e in examples}
        for identity in fold.training_ids:
            example = by[identity]
            probability, served = base.predict(example)
            manifest = graph.manifest_node(served["actual_read_manifest"])
            p = min(1 - model.probability_floor, max(model.probability_floor, probability))
            logit = math.log(p) - math.log1p(-p)
            known = max(record.row.input_known_at for record in manifest.read_manifest.reads)
            observed = max(record.row.observed_at for record in manifest.read_manifest.reads)
            end = sample_target_end(example.sample)
            prediction = PredictionEvidence(identity, target_ref, example.sample.decision_at,
                end, example.sample.decision_at, example.sample.decision_at, known,
                base.model_node_id, manifest.id, "OOF")
            logits[identity] = graph.node(prefix + ":base-oof:" + identity, "oof_prediction",
                rows=(RowEvidence(identity, "raw_logit", digest((model.base.id, manifest.id, p)),
                    manifest.id, observed, known, "derived", canonical_json(logit), valid_until=end),),
                prediction_evidence=prediction,
                dependencies=(DependencyRef("fit", base.model_node_id, "provenance"),
                              DependencyRef("reads", manifest.id, "provenance")),
                execution=graph.execution({"operation": "sigmoid_calibration_raw_logit",
                    "base_probability": probability, "probability_floor": model.probability_floor}))
        predictions = graph.commit(prefix + ":oof-calibration-inputs",
            (fold_node.id, labels.id, source.id, *(n.id for n in logits.values()), *upstream_roots))
        logit_manifests = _training_reads(graph, predictions, logits, fold_node, examples, ("raw_logit",))
        calibration_node = _simple_model(graph, model.calibration, fold_node, labels, logit_manifests, examples)
        fit = _fit_evidence(graph, fold_node, labels, raw_manifests, examples)
        fitted_node = graph.node("e0:model:" + model.id, "calibrator", raw=canonical_json(model),
            fit_evidence=fit,
            dependencies=_fit_dependencies(fold_node, labels, raw_manifests,
                (graph.nodes[base.model_node_id], calibration_node)),
            execution=graph.execution({"input_columns": model.base.columns,
                "research_scope": getattr(model, "_research_scope", None),
                "role": "separate_sigmoid_calibrated_binary", "model_id": model.id}))
    commit = graph.commit(prefix + ":fitted", (fitted_node.id, source.id))
    binding = E0ModelBinding(store, commit, fitted_node.id, source.id, fold_node.id, target_ref, model.id)
    # Reopening recomputes scaler moments or conditional cell counts from the
    # exact retained training reads before this binding can escape the port.
    if canonical_json(binding.reopen()) != canonical_json(model):
        raise IntegrityError("E0 committed model differs from the supplied fitted state")
    return binding


def commit_e0_fit(store, *, namespace, code_ref, target_ref, definition_ref,
                  payloads, examples, fit):
    """Commit an E0BinaryFit and return its actual-store prediction callback."""
    from trading_research.experiments.e0.learning import E0BinaryFit, E0LearningConfig, e0_stages
    if type(fit) is not E0BinaryFit:
        raise ContractError("E0 complete fit binding requires the actual typed stage result")
    examples = tuple(examples)
    if type(fit.config) is not E0LearningConfig:
        raise ContractError("E0 committed fit requires its exact typed configuration")
    fit.config.__post_init__()
    if (type(target_ref) is not ArtifactRef or target_ref.sha256 != fit.config.target_version
            or fit.config.target_payload is None
            or payloads.get(target_ref.sha256) != fit.config.target_payload
            or payload_ref(fit.config.target_payload, target_ref.kind) != target_ref):
        raise ContractError("E0 committed target bytes differ from the configured policy and head")
    if any(type(e) is not BinaryExample for e in examples):
        raise ContractError("E0 committed stage population requires exact binary examples")
    if e0_stages(tuple(e.sample for e in examples), fit.config) != fit.stages:
        raise ContractError("E0 committed stages differ from their complete configured population")
    bindings = {}
    common = dict(namespace=namespace, code_ref=code_ref, target_ref=target_ref,
                  definition_ref=definition_ref, payloads=payloads, examples=examples)
    for model in (fit.frequency, *fit.logistic_candidates, fit.selected):
        if model.id not in bindings:
            bindings[model.id] = commit_e0_binary(store, **common, fold=fit.stages.fit_fold, model=model)
    if fit.calibrated.id not in bindings:
        if type(fit.calibrated) is not CalibratedBinary:
            raise ContractError("E0 unknown fallback or calibration component")
        base = bindings.get(fit.calibrated.base.id)
        if base is None:
            raise ContractError("E0 calibrated model has no retained selected base")
        bindings[fit.calibrated.id] = commit_e0_binary(store, **common,
            fold=fit.stages.calibration_fold, model=fit.calibrated, upstream_bindings=(base,))
    return E0CommittedBinaryFit(tuple(bindings.values()), fit.version)
