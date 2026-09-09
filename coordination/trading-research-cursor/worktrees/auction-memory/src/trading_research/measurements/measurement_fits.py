"""Actual F11/TemporalFold boundary for fitted measurement publication.

Numerical kernels may return unpublished state. Serving reopens the exact
committed closure, checks original OOF requests, and reconstructs that state
from retained training reads and actual measurement captures.
"""

from dataclasses import dataclass, field, replace
from fractions import Fraction
import json

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.artifact_graph import (
    CommitRef, ReadRequest, SemanticArtifactStore, ValidatedTemporalFoldEvidenceV1,
    training_standardization, validate_oof_producer,
)
from trading_research.research.period import (PrimaryAdmissionV1, ResearchPeriodPolicyV1,
    ResearchScopeV1, check_sample_population, validate_consumer_admission_shape,
    validate_primary_admission, validate_scope)
from trading_research.research.temporal_folds import validate_temporal_fold_population


@dataclass(frozen=True)
class MeasurementFitAdmission:
    commit_ref: CommitRef
    node_id: str
    request: ReadRequest
    schema_id: str
    unit: str
    recipe_id: str
    max_training_rows: int
    population: tuple
    fold: object
    training_manifests: tuple
    payload: bytes
    configuration: bytes
    actual_fit_completion_at: int
    _store: object = field(default=None, init=False, repr=False, compare=False)


def admit_measurement_fit(store, commit_ref, node_id, request, *, schema_id, unit, recipe_id,
                          max_training_rows=1024, scope: ResearchScopeV1 | None = None,
                          policy: ResearchPeriodPolicyV1 | None = None,
                          admission: PrimaryAdmissionV1 | None = None):
    positive_limit(max_training_rows)
    for value in (node_id, schema_id, unit, recipe_id):
        bounded_name(value)
    if type(store) is not SemanticArtifactStore or type(commit_ref) is not CommitRef or type(request) is not ReadRequest:
        raise ContractError("measurement fit needs an actual semantic store, exact commit and typed original request")
    if request.purpose not in ("OOF", "fit_feature", "final"):
        raise ContractError("audit/raw-input reads cannot authorize fitted measurement serving")
    if (request.schema_id, request.unit) != (schema_id, unit):
        raise ContractError("fitted measurement request schema/unit differs")
    verified = store.read_commit(commit_ref.key)
    if verified.reference != commit_ref:
        raise IntegrityError("fitted measurement commit reference changed")
    node = verified.closure.by_id.get(node_id)
    if node is None or node.kind != "transform" or node.fit_evidence is None or node.execution is None:
        raise ContractError("retained fitted transform required")
    if (node.schema_id, node.unit) != (schema_id, unit):
        raise ContractError("retained transform schema or unit differs")
    fit = node.fit_evidence
    evidence = verified.closure.by_id[fit.fold_node_id].fold_evidence
    if type(evidence) is not ValidatedTemporalFoldEvidenceV1:
        raise ContractError("measurement fits require the actual complete temporal population/fold")
    validate_scope(scope, policy)
    admission_cut = validate_consumer_admission_shape(scope=scope, policy=policy, admission=admission)
    check_sample_population(scope, policy, evidence.population, fit_at=evidence.fold.fit_at,
                            evaluation_start=evidence.fold.evaluation_start,
                            evaluation_end=evidence.fold.evaluation_end,
                            training_start=evidence.fold.training_start,
                            actual_cut_at=admission_cut)
    if scope is not None and scope.is_primary:
        validate_primary_admission(admission, evidence.population, scope=scope, policy=policy)  # type: ignore[arg-type]
    elif admission is not None:
        raise ContractError("population admission envelope is only valid for an explicit primary scope")
    if scope is not None:
        validate_temporal_fold_population(evidence.population, evidence.fold, scope=scope,
                                          policy=policy, admission=admission)
    bounded_rows(fit.training_sample_ids, max_training_rows, name="measurement training membership")
    bounded_rows(fit.actual_training_read_manifests, max_training_rows, name="measurement training manifests")
    if fit.actual_fit_completion_at > request.decision_cut:
        raise ContractError("measurement fit completes after its inference cut")
    # Final/future serving uses the same declared original evaluation population;
    # a string mode does not remove date/episode/ancestor exclusion.
    validate_oof_producer(request, node_id, verified)
    config = json.loads(node.execution.configuration_json)
    recipe = config.get("measurement_fit") if type(config) is dict else None
    if type(recipe) is not dict or recipe.get("recipe_id") != recipe_id:
        raise IntegrityError("measurement recipe differs from actual retained execution configuration")
    manifests = tuple(verified.closure.by_id[i].read_manifest for i in fit.actual_training_read_manifests)
    result = MeasurementFitAdmission(commit_ref, node_id, request, schema_id, unit, recipe_id, max_training_rows,
        evidence.population, evidence.fold, manifests, verified.closure._payloads[node.payload_ref.sha256],
        node.execution.configuration_json, fit.actual_fit_completion_at)
    object.__setattr__(result, "_store", store)
    object.__setattr__(result, "_research_scope", scope)
    object.__setattr__(result, "_period_policy", policy)
    object.__setattr__(result, "_primary_admission", admission)
    return result


def _reopen(admission):
    if type(admission) is not MeasurementFitAdmission or type(admission._store) is not SemanticArtifactStore:
        raise ContractError("actual fitted admission recipe required")
    fresh = admit_measurement_fit(admission._store, admission.commit_ref, admission.node_id, admission.request,
        schema_id=admission.schema_id, unit=admission.unit, recipe_id=admission.recipe_id,
        max_training_rows=admission.max_training_rows, scope=admission._research_scope,
        policy=admission._period_policy, admission=admission._primary_admission)
    if fresh != admission:
        raise IntegrityError("measurement fit admission changed from actual retained training closure")
    return fresh


def validate_measurement_fit_payload(admission, reconstructed_bytes):
    fresh = _reopen(admission)
    if type(reconstructed_bytes) is not bytes or reconstructed_bytes != fresh.payload:
        raise IntegrityError("reconstructed fitted measurement differs from retained parameters")
    return fresh


def standardize_from_measurement_fit(admission, *, columns, values, query_session):
    """Small actual-store integration port; feature-family inputs have their own adapters."""
    admission = _reopen(admission)
    bounded_rows(columns, 16, name="standardization columns")
    bounded_rows(values, 16, name="standardization values")
    if type(columns) is not tuple or len(columns) != len(values) or not columns:
        raise ContractError("standardization needs identical nonempty column/value dimensions")
    verified = admission._store.read_commit(admission.commit_ref.key)
    if verified.reference != admission.commit_ref:
        raise IntegrityError("standardization commit changed")
    means, scales = training_standardization(verified, admission.node_id, columns)
    reconstructed = canonical_json({"columns": columns, "means": means, "scales": scales})
    validate_measurement_fit_payload(admission, reconstructed)
    query = read_measurement_query(admission, query_session, window_start=admission.request.decision_cut, columns=columns)
    if canonical_json(tuple(query[k] for k in columns)) != canonical_json(tuple(values)):
        raise IntegrityError("standardization values differ from the actual original query reads")
    from trading_research.research.scoring import finite
    return tuple((finite(v) - m) / s for v, m, s in zip(values, means, scales))


@dataclass(frozen=True)
class MeasurementFitBinding:
    admission: MeasurementFitAdmission
    training_captures: tuple
    prewindow_contexts: tuple = ()
    query_session: object = field(default=None, compare=False, repr=False)


def _json_exact(raw):
    def hook(value):
        if set(value) == {"$fraction"}:
            return Fraction(*value["$fraction"])
        return value
    return json.loads(raw, object_hook=hook)


def _training_captures(binding, view):
    admission = _reopen(binding.admission)
    bounded_rows(binding.training_captures, admission.max_training_rows, name="bound training captures")
    bounded_rows(binding.prewindow_contexts, admission.max_training_rows, name="bound training contexts")
    if type(binding.training_captures) is not tuple or type(binding.prewindow_contexts) is not tuple:
        raise ContractError("measurement fit source recipes must be immutable")
    for pair in (*binding.training_captures, *binding.prewindow_contexts):
        if type(pair) is not tuple or len(pair) != 2:
            raise ContractError("training source recipe must pair original row identity and actual evidence")
        bounded_name(pair[0])
    by = dict(binding.training_captures)
    contexts = dict(binding.prewindow_contexts)
    if (len(by) != len(binding.training_captures) or len(contexts) != len(binding.prewindow_contexts)
            or set(by) != set(admission.fold.training_ids) or not set(contexts) <= set(by)):
        raise ContractError("bound source captures differ from complete actual temporal training membership")
    manifests = {m.bindings[0].request.row_id: m for m in admission.training_manifests}
    population = {s.id: s for s in admission.population}
    for row_id, capture in by.items():
        validate_trade_window(capture, view)
        sample = population[row_id]
        if capture.window.published_at > sample.decision_at or capture.window.cut > sample.decision_at:
            raise ContractError("measurement training input was unavailable at its original row cut")
        reads = {r.binding.column: r for r in manifests[row_id].reads}
        retained = reads.get("measurement_capture")
        if retained is None or retained.row.value_json != canonical_json(capture.record()):
            raise IntegrityError("training capture is not the exact actual retained input read")
        if row_id in contexts:
            context_read = reads.get("prewindow_context")
            if context_read is None or context_read.row.value_json != canonical_json(contexts[row_id]):
                raise IntegrityError("conditional context differs from actual retained prewindow read")
    return admission, by, contexts


def validate_measurement_fit(binding, *, capture, view, family, state, context=None, epsilon=None):
    if type(binding) is not MeasurementFitBinding:
        raise ContractError("fitted measurement needs actual source-bound training admission")
    validate_trade_window(capture, view)
    admission, by, contexts = _training_captures(binding, view)
    w, request = capture.window, admission.request
    if request.decision_cut != w.cut or request.assembled_at != w.published_at:
        raise ContractError("fitted feature request differs from original measurement window")
    if admission.actual_fit_completion_at > w.start:
        raise DependencyUnavailable("fitted feature was unavailable before the measurement window")
    recipe = _json_exact(admission.configuration)["measurement_fit"]
    if recipe.get("family") != family or type(recipe.get("parameters")) is not dict:
        raise ContractError("retained fitted family/recipe differs")
    parameters = recipe["parameters"]
    columns = ('measurement_capture',) + (('prewindow_context',) if family in ('conditional_flow', 'effort_surface') else ())
    query = read_measurement_query(admission, binding.query_session, window_start=w.start, columns=columns)
    if canonical_json(query['measurement_capture']) != canonical_json(capture.record()):
        raise IntegrityError("fitted inference capture differs from the actual query reads")
    if 'prewindow_context' in query and canonical_json(query['prewindow_context']) != canonical_json(context):
        raise IntegrityError("fitted inference context differs from the actual query reads")
    if family == 'effort_surface' and epsilon != parameters.get('epsilon'):
        raise ContractError("inference effort epsilon differs from the retained fit recipe")
    captures = tuple(by[i] for i in admission.fold.training_ids)
    if family == "cohort":
        from trading_research.measurements.cvd import fit_cohort_definition
        allowed = {"train_end", "available_at", "probabilities", "weighting", "version"}
        if set(parameters) != allowed:
            raise ContractError("cohort retained recipe fields differ")
        reconstructed = fit_cohort_definition(captures, view=view, max_training_rows=admission.max_training_rows,
                                              **parameters)["definition"]
        identity = reconstructed.fit_recipe_id
    elif family == "conditional_flow":
        from trading_research.measurements.tape_intensity import fit_conditional_flow
        allowed = {"train_end", "available_at", "version", "minimum_cell_rows"}
        if set(parameters) != allowed or set(contexts) != set(by):
            raise ContractError("conditional-flow retained context/recipe fields differ")
        rows = tuple((by[i], contexts[i]) for i in admission.fold.training_ids)
        reconstructed = fit_conditional_flow(rows, view=view, max_training_rows=admission.max_training_rows, **parameters)
        identity = reconstructed.recipe_id
    elif family == "effort_surface":
        from trading_research.measurements.tape_intensity import fit_effort_progress_surface, measure_tape_intensity
        allowed = {"effort_cuts", "volatility_cuts", "shrinkage", "available_at", "version", "epsilon"}
        if set(parameters) != allowed or set(contexts) != set(by):
            raise ContractError("effort-surface retained context/recipe fields differ")
        rows = []
        for row_id in admission.fold.training_ids:
            context = contexts[row_id]
            if type(context) is not tuple or len(context) != 2 or context[0] > by[row_id].window.start:
                raise ContractError("surface volatility requires its actual prewindow availability")
            measurement = measure_tape_intensity(by[row_id], view=view, epsilon=parameters["epsilon"])
            if measurement.progress_ticks is None:
                raise DependencyUnavailable("surface training progress is not observed")
            rows.append((measurement.gross_effort, context[1], measurement.progress_ticks))
        reconstructed = fit_effort_progress_surface(tuple(rows), max_training_rows=admission.max_training_rows,
            **{k: v for k, v in parameters.items() if k != "epsilon"})
        identity = reconstructed.recipe_id
    else:
        raise DependencyUnavailable("family needs its concrete retained-training reconstruction adapter")
    if identity != admission.recipe_id or reconstructed != state:
        raise IntegrityError("fitted measurement state/recipe differs from actual admitted training rows")
    validate_measurement_fit_payload(admission, canonical_json(reconstructed))
    return admission


def read_measurement_query(admission, session, *, window_start, columns):
    """Resolve each query value through the actual F11 source session."""
    from trading_research.operations.artifact_graph import ReadSession
    from trading_research.foundations.time import timestamp
    admission = _reopen(admission)
    timestamp(window_start)
    bounded_rows(columns, 32, name="fitted query columns")
    if type(session) is not ReadSession or not columns or len(set(columns)) != len(columns):
        raise ContractError("fitted query needs an actual declared source read session")
    config = session._configuration
    if (config.store.namespace != admission._store.namespace
            or config.store.configuration_id != admission._store.configuration_id):
        raise ContractError("fitted query source store differs")
    if admission.actual_fit_completion_at > window_start:
        raise DependencyUnavailable("fit was unavailable before the queried measurement began")
    query_commit = config.store.read_commit(config.commit_ref.key)
    if query_commit.reference != config.commit_ref:
        raise IntegrityError("query commit reference changed")
    bindings = {b.column: b for b in session.bindings}
    request = admission.request
    for column in columns:
        b = bindings.get(column)
        if b is None:
            raise ContractError("query input was not declared in its actual read session")
        q = b.request
        if replace(q, purpose=request.purpose) != request:
            raise ContractError("query input uses another original sample, cut or temporal route")
        if q.purpose not in ("input", request.purpose):
            raise ContractError("query input has an incompatible temporal read purpose")
        pending, visited, fitted = [b.node_id], set(), False
        while pending:
            identity = pending.pop()
            if identity in visited:
                continue
            visited.add(identity)
            node = query_commit.closure.by_id.get(identity)
            if node is None:
                raise IntegrityError("query source dependency is absent from its actual closure")
            fitted |= node.fit_evidence is not None
            pending.extend(edge.source_id for edge in node.dependencies)
        if fitted:
            validate_oof_producer(replace(q, purpose=request.purpose), b.node_id, query_commit)
        # Replay resolution even when a session has already been sealed.
        actual = config.store.resolve(config.commit_ref, b.node_id, b.source_column, b.request)
        old = session._reads.get(column)
        if old is not None and old.row != actual:
            raise IntegrityError("query read bytes differ from the actual retained source")
        if session._sealed is None:
            session.read(column)
        elif old is None:
            raise ContractError("sealed query omitted a required fitted input")
    return {column: _json_exact(config.store.resolve(config.commit_ref, bindings[column].node_id,
        bindings[column].source_column, bindings[column].request).value_json) for column in columns}


def reconstruct_numeric_measurement_fit(admission, *, family):
    """Compact residual/distance kernels reconstructed from complete retained reads."""
    admission = _reopen(admission)
    recipe = _json_exact(admission.configuration)["measurement_fit"]
    parameters = recipe.get("parameters")
    if recipe.get("family") != family or type(parameters) is not dict:
        raise ContractError("numeric measurement family or retained recipe differs")
    manifests = {m.bindings[0].request.row_id: m for m in admission.training_manifests}
    if set(manifests) != set(admission.fold.training_ids):
        raise IntegrityError("numeric fit does not retain the complete admitted training population")
    if family in ("divergence_residual", "quote_lag"):
        allowed = {"x_columns", "lag_column", "y_column", "basis", "ridge", "train_end", "available_at"}
        if set(parameters) != allowed:
            raise ContractError("ridge measurement retained parameter fields differ")
        from trading_research.measurements.divergence import fit_divergence_residual
        verified = admission._store.read_commit(admission.commit_ref.key)
        fit = verified.closure.by_id[admission.node_id].fit_evidence
        labels = {l.row_id: l for l in fit.training_label_refs}
        rows = []
        bounded_rows(parameters["x_columns"], 16, name="ridge retained feature columns")
        for row_id in admission.fold.training_ids:
            reads = {r.binding.column: r.row for r in manifests[row_id].reads}
            columns = tuple(parameters["x_columns"]) + (parameters["lag_column"],)
            if any(c not in reads for c in columns) or row_id not in labels:
                raise IntegrityError("ridge fit lacks actual retained inputs or matured target")
            label = labels[row_id]
            node = verified.closure.by_id[label.label_node_id]
            matches = [r for r in node.row_evidence if r.row_id == row_id and r.column == label.column]
            if len(matches) != 1:
                raise IntegrityError("ridge target does not resolve to one actual retained label")
            y = _json_exact(matches[0].value_json)
            x = tuple(_json_exact(reads[c].value_json) for c in parameters["x_columns"])
            lag = _json_exact(reads[parameters["lag_column"]].value_json)
            known = max(matches[0].input_known_at, *(reads[c].input_known_at for c in columns))
            rows.append((row_id, x, lag, y, known))
        state = fit_divergence_residual(tuple(rows), train_end=parameters["train_end"],
            available_at=parameters["available_at"], ridge=parameters["ridge"], basis=tuple(parameters["basis"]),
            max_training_rows=admission.max_training_rows)
        if state.recipe_id != admission.recipe_id:
            raise IntegrityError("ridge source reconstruction changes the retained recipe identity")
    elif family == "memory_distance":
        if set(parameters) != {"columns"}:
            raise ContractError("memory distance retained parameter fields differ")
        columns = tuple(parameters["columns"])
        bounded_rows(columns, 16, name="memory distance columns")
        verified = admission._store.read_commit(admission.commit_ref.key)
        means, scales = training_standardization(verified, admission.node_id, columns)
        state = {"columns": columns, "means": means, "scales": scales}
    else:
        raise DependencyUnavailable("unregistered numeric measurement reconstruction")
    validate_measurement_fit_payload(admission, canonical_json(state))
    return state, parameters
