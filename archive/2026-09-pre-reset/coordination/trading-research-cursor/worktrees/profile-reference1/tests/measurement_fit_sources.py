"""Real retained F11 training/label/query fixtures for measurement integration."""

from dataclasses import fields, replace
from pathlib import Path

from trading_research.operations.artifacts import canonical_json
from trading_research.operations.artifact_graph import (
    SemanticArtifactStore, ReadRequest, ReadBinding, ReadSession, FitEvidence, LabelEvidence, LabelTarget,
    validate_temporal_fold_evidence,
)
from trading_research.research.temporal_folds import DEFAULT_LIMITS, TemporalSampleV1, compile_temporal_fold
from trading_research.measurements.measurement_fits import admit_measurement_fit
from tests.test_artifact_graph import Fixture


SCHEMA, UNIT = "MeasurementFixture.v1", "descriptive_measurement"


def fitted_sources(root, *, family, parameters, recipe_id, state, training_features,
                   query_features, training_labels=(-2, 2), completion=31, training_ids=None,
                   fit_payload=None, query_start=39, clock_offset=0):
    f = Fixture()
    f.namespace = "measurement-fit:"+family
    f.target = f.keep(b"registered-measurement-conditional-target-v1", "target")
    population = tuple(TemporalSampleV1(identity, group, cut+clock_offset, end+clock_offset, known+clock_offset, f.target.sha256, role, episode, (), ())
        for identity, group, cut, end, known, role, episode in (
            ("train1", "date1", 10, 11, 12, "train", "episode1"),
            ("train2", "date2", 20, 21, 22, "train", "episode2"),
            ("heldout", "date3", 40, 50, 51, "outer", "episode3")))
    fold = compile_temporal_fold(population, id="measurement-fit-fold", fit_at=30+clock_offset, evaluation_start=40+clock_offset, evaluation_end=60+clock_offset)
    fold_node = f.node("fold", "fold", execution=replace(f.execution, configuration_json=canonical_json({
        "temporal_limits_v1": {field.name: getattr(DEFAULT_LIMITS, field.name) for field in fields(DEFAULT_LIMITS)},
    })), fold_evidence=validate_temporal_fold_evidence(population, fold), schema_id=SCHEMA, unit=UNIT)
    values = (*training_features, query_features)
    source = f.node("sources", "source", schema_id=SCHEMA, unit=UNIT, rows=tuple(
        f.row(row_id=s.id, column=k, value=v, observed=s.decision_at-1, known=s.decision_at,
              version="source:"+s.id+":"+k, acquisition="receipt:"+s.id, valid_until=60+clock_offset)
        for s, columns in zip(population, values) for k, v in columns.items()))
    labels = f.node("labels", "label", schema_id=SCHEMA, unit=UNIT, rows=tuple(
        f.row(row_id=s.id, column="label", value=v, observed=s.target_end, known=s.label_known_at,
              version="label:"+s.id, acquisition="label-receipt:"+s.id, valid_until=60+clock_offset)
        for s, v in zip(population[:2], training_labels)),
        label_targets=tuple(LabelTarget(s.id, f.target, s.decision_at, s.target_end) for s in population[:2]))
    store = SemanticArtifactStore(Path(root), f.namespace)
    source_nodes = (fold_node, source, labels)
    base = store.commit("inputs", tuple(n.id for n in source_nodes), source_nodes, f.payloads)
    read_nodes = []
    for sample, columns in zip(population[:2], training_features):
        request = ReadRequest(sample.id, sample.decision_at, sample.decision_at, "fit_feature", SCHEMA, UNIT,
            date_group=sample.date_group, fold_node_id=fold_node.id)
        bindings = tuple(ReadBinding(k, source.id, k, request) for k in sorted(columns))
        session = ReadSession(store, base, bindings)
        for k in sorted(columns):
            session.read(k)
        read_nodes.append(f.node("reads:"+sample.id, "read_manifest", schema_id=SCHEMA, unit=UNIT,
            read_manifest=session.seal(), dependencies=(*(f.dep(k, source, "value", (k,)) for k in sorted(columns)),
                                                       f.dep("fold", fold_node))))
    fit = FitEvidence(fold_node.id, 30+clock_offset, completion+clock_offset, fold.training_ids if training_ids is None else training_ids,
        ("date1", "date2"), tuple(LabelEvidence(s.id, labels.id, "label", f.target) for s in population[:2]),
        tuple(n.id for n in read_nodes), f.target)
    execution = replace(f.execution, configuration_json=canonical_json({
        "measurement_fit": {"family": family, "recipe_id": recipe_id, "parameters": parameters},
    }))
    payload = canonical_json(state) if fit_payload is None else fit_payload
    transform = f.node("measurement-transform", "transform", schema_id=SCHEMA, unit=UNIT, raw=payload,
        execution=execution, fit_evidence=fit, dependencies=(f.dep("fold", fold_node),
            f.dep("labels", labels, "fit_label", ("label",)), *(f.dep(n.logical_key, n) for n in read_nodes)))
    nodes = (*source_nodes, *read_nodes, transform)
    commit = store.commit("fitted", (transform.id,), nodes, f.payloads)
    request = ReadRequest("heldout", 40+clock_offset, 41+clock_offset, "OOF", SCHEMA, UNIT, f.target, 40+clock_offset, 50+clock_offset, "date3", fold_node.id)
    admission = admit_measurement_fit(store, commit, transform.id, request, schema_id=SCHEMA, unit=UNIT, recipe_id=recipe_id)
    query_session = ReadSession(store, base, tuple(ReadBinding(k, source.id, k, replace(request, purpose="input")) for k in sorted(query_features)))
    return {"store": store, "commit": commit, "transform": transform, "request": request, "admission": admission,
        "query_session": query_session, "source": source, "fold_node": fold_node, "base": base, "payload": payload,
        "recipe_id": recipe_id, "query_start": query_start}
