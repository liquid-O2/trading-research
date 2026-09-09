"""Actual retained-read parity and tamper controls inside INT10-F03 only."""

from dataclasses import replace
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import canonical_json
from trading_research.operations.artifact_graph import (
    ReadBinding, ReadRequest, ReadSession, SemanticArtifactStore,
    restore_bound_model, serve_bound_model,
    _VerifiedReadOperation,
)
from trading_research.operations.artifact_graph_reference import reference_serve_bound_model


def check_e0_serving_operation(test, router, evaluation_date):
    head = router.policies[0][1][0]
    example = next(row for row in head.examples if row.sample.date_group == evaluation_date)
    model = head.fit.calibrated
    binding = head.committed.binding(model)
    store, commit_ref = binding.store, binding.commit_ref
    sample = example.sample
    request = ReadRequest(sample.id, sample.decision_at, sample.decision_at, "OOF",
        "E0BinaryInputs.v1", "declared_numeric_feature", binding.target_ref,
        sample.decision_at, sample.dependency_end, sample.date_group, binding.fold_node_id)
    columns = model.base.columns
    bindings = tuple(ReadBinding(column, binding.source_node_id, column, request) for column in columns)
    with test.assertRaisesRegex(ContractError, "active store scope"):
        _VerifiedReadOperation(store, commit_ref)

    before = store.io_counts
    started = time.process_time()
    reference = reference_serve_bound_model(model, store, commit_ref, binding.model_node_id,
                                             ReadSession(store, commit_ref, bindings))
    reference_cpu = time.process_time() - started
    reference_reads = store.io_counts["read_calls"] - before["read_calls"]
    before = store.io_counts
    started = time.process_time()
    with store.read_operation(commit_ref) as operation:
        retained = restore_bound_model(store, commit_ref, binding.model_node_id, read_operation=operation)
        actual = serve_bound_model(retained, store, commit_ref, binding.model_node_id,
            ReadSession(store, commit_ref, bindings, read_operation=operation))
        closure = operation.read_commit(store, commit_ref).closure
        with test.assertRaises(TypeError):
            closure._payloads[binding.target_ref.sha256] = b"changed"
        with test.assertRaises(AttributeError):
            operation._closed = False
        with test.assertRaises(IntegrityError):
            operation.read_commit(store, replace(commit_ref, key=commit_ref.key + ":wrong"))
        with test.assertRaisesRegex(ContractError, "cannot mutate"):
            store.commit("forbidden-inside-read", (), (), {})
    operation_cpu = time.process_time() - started
    operation_reads = store.io_counts["read_calls"] - before["read_calls"]
    test.assertEqual(canonical_json(actual), canonical_json(reference))
    test.assertEqual(actual[0], .5)
    test.assertEqual(len(actual[1].reads), len(columns))
    test.assertLess(operation_reads, reference_reads)
    with test.assertRaisesRegex(ContractError, "closed"):
        operation.read_commit(store, commit_ref)

    reopened_store = SemanticArtifactStore(store.root, store.namespace, store.limits)
    with store.read_operation(commit_ref) as operation:
        with test.assertRaises(IntegrityError):
            ReadSession(reopened_store, commit_ref, bindings, read_operation=operation)
        wrong_request = replace(request, date_group="2025-01-01")
        wrong_bindings = tuple(replace(row, request=wrong_request) for row in bindings)
        with test.assertRaises(ContractError):
            serve_bound_model(model, store, commit_ref, binding.model_node_id,
                ReadSession(store, commit_ref, wrong_bindings, read_operation=operation))

    # An unrelated filesystem writer does not take the cooperative read lock.
    # The scope must detect that mutation before returning the computed value.
    retained_path = store._blobs.path(binding.target_ref)
    original = retained_path.read_bytes()
    changed = bytes((original[0] ^ 1,)) + original[1:]
    try:
        with test.assertRaises(IntegrityError):
            with store.read_operation(commit_ref) as operation:
                retained_path.write_bytes(changed)
                serve_bound_model(model, store, commit_ref, binding.model_node_id,
                    ReadSession(store, commit_ref, bindings, read_operation=operation))
    finally:
        retained_path.write_bytes(original)
    # A new operation cannot reuse a previous successful snapshot after a
    # between-operation mutation, either.
    try:
        retained_path.write_bytes(changed)
        with test.assertRaises(IntegrityError):
            binding.predict(example)
    finally:
        retained_path.write_bytes(original)
    test.assertEqual(binding.predict(example)[0], reference[0])
    changed_calibration = replace(model.calibration,
        intercept=model.calibration.intercept + 1)
    with test.assertRaises(IntegrityError):
        binding(replace(model, calibration=changed_calibration), example)
    return {"reference_read_calls": reference_reads, "operation_read_calls": operation_reads,
            "reference_cpu_seconds": reference_cpu, "operation_cpu_seconds": operation_cpu,
            "probability": actual[0], "actual_read_manifest_id": actual[1].id}
