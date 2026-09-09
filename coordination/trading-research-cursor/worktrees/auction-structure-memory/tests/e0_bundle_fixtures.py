"""Bundle assertions called only inside the registered INT10-F03 family."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path

from trading_research.__main__ import main
from trading_research.errors import ContractError, IntegrityError
from trading_research.experiments.e0.bundle import write_e0_bundle, load_e0_bundle
from trading_research.operations.artifacts import canonical_json


def check_e0_bundle(test, root, manifest, days, router, input_artifacts):
    path = write_e0_bundle(Path(root) / "exported-e0", manifest, days, router, input_artifacts)
    loaded_manifest, loaded_days, loaded_router = load_e0_bundle(path)
    test.assertEqual(canonical_json(loaded_manifest), canonical_json(manifest))
    test.assertEqual(canonical_json(loaded_days), canonical_json(days))
    test.assertEqual(loaded_router.version, router.version)
    output = io.StringIO()
    with redirect_stdout(output):
        test.assertEqual(main(["e0-check", "--bundle", str(path)]), 0)
    summary = json.loads(output.getvalue())
    test.assertTrue(summary["success"])
    test.assertEqual((summary["logical_runs"], summary["fits_performed"], summary["replays_performed"]), (64, 0, 0))

    # Reopen and serve the same actual held-out row through the retained F11 port.
    original = router.policies[0][1][0]
    restored = loaded_router.policies[0][1][0]
    example = next(row for row in original.examples if row.sample.date_group == days[0].day)
    restored_example = next(row for row in restored.examples if row.sample.id == example.sample.id)
    before = original.committed(original.fit.calibrated, example)
    after = restored.committed(restored.fit.calibrated, restored_example)
    test.assertEqual(canonical_json(before), canonical_json(after))

    saved = path.read_bytes()
    envelope = json.loads(saved)
    def reject(mutated):
        path.write_bytes(json.dumps(mutated, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
        try:
            with test.assertRaises((ContractError, IntegrityError, OSError)):
                load_e0_bundle(path)
        finally:
            path.write_bytes(saved)
    bad = deepcopy(envelope)
    bad["payload"]["items"][0]["fields"]["day_versions"]["items"][0] = "changed-after-freeze"
    reject(bad)
    bad = deepcopy(envelope)
    bad["inventory"][0]["path"] = "../outside"
    reject(bad)
    bad = deepcopy(envelope)
    bad["payload"]["items"][0]["fields"]["unregistered_field"] = 1
    reject(bad)
    for relative in ("inputs/native_sources.json", "inputs/code_snapshot.json"):
        retained = path.parent / relative
        data = retained.read_bytes()
        retained.write_bytes(data + b" ")
        try:
            with test.assertRaises(IntegrityError):
                load_e0_bundle(path)
        finally:
            retained.write_bytes(data)
    return summary


def check_e0_supervision(test, root, *, matrix_root):
    """Use the existing actual matrix and structural lifecycle controls only."""
    import os
    import time
    from trading_research.__main__ import (_E0_LIMITS, _e0_resource_error, _finalize_e0_supervision,
        _join_e0_supervision, _matrix_summary, _process_identity, _recover_e0)
    from trading_research.operations.artifacts import digest, publish_new
    from trading_research.operations.trials import TrialRegistry
    root = Path(root).absolute()
    root.mkdir(parents=True, exist_ok=True)
    test.assertIsNone(_e0_resource_error(1., 2., 1024))
    for cpu, wall, rss in ((180, 2., 1024), (180.0001, 2., 1024), (1., 360, 1024),
                          (1., 2., 4 * 1024 ** 3), (None, 2., 1024), (True, 2., 1024),
                          (float("nan"), 2., 1024), (float("inf"), 2., 1024),
                          (1., float("nan"), 1024), (1., 2., 1024.), (1., 2., True),
                          (0., 2., 1024), (1., 0., 1024), (1., 2., 0)):
        with test.subTest(resource_boundary=(cpu, wall, rss)):
            test.assertIsNotNone(_e0_resource_error(cpu, wall, rss))
    matrix = _matrix_summary(Path(matrix_root))
    output = io.StringIO()
    with redirect_stdout(output):
        test.assertEqual(main(["e0-report", "--output-root", str(matrix_root)]), 0)
    report = json.loads(output.getvalue())
    test.assertEqual(report["matrix_artifact"], matrix["matrix_artifact"])
    test.assertFalse(report["physical_resources_accepted"])
    # These are explicit in-memory boundary inputs, not retained physical
    # measurements. The inner result is the existing real matrix artifact.
    joined_input = {"status": "succeeded", "exit_code": 0, "resource_basis": "observed_wait4",
        **{key: matrix[key] for key in ("physical_attempt", "matrix_artifact", "manifest_version")},
        **matrix["matrix_resources"]}
    joined = _join_e0_supervision(joined_input, matrix)
    test.assertTrue(joined["physical_resources_accepted"])
    test.assertEqual(joined["matrix_artifact"], matrix["matrix_artifact"])
    for field, value in (("cpu_seconds", 180), ("wall_seconds", 360), ("peak_rss_bytes", 4 * 1024 ** 3),
                         ("physical_attempt", "changed"), ("manifest_version", "changed"),
                         ("matrix_artifact", {}), ("resource_basis", "reservation_charged_usage_unknown"),
                         ("exit_code", True)):
        with test.subTest(supervisor_join=field), test.assertRaises(IntegrityError):
            _join_e0_supervision({**joined_input, field: value}, matrix)
    bad_inner = {**matrix, "matrix_resources": {**matrix["matrix_resources"],
                 "cpu_seconds": joined_input["cpu_seconds"] + 1}}
    with test.assertRaises(IntegrityError):
        _join_e0_supervision(joined_input, bad_inner)

    def request(directory):
        directory.mkdir()
        value = {"schema": "E0SupervisionV2", "status": "started", "bundle": str(directory / "absent-bundle"),
                 "output_root": str(directory.absolute()), "started_at_utc_ns": time.time_ns(),
                 "supervisor": _process_identity(os.getpid()), **_E0_LIMITS,
                 "maximum_physical_workers": 1, "maximum_logical_runs": 64}
        publish_new(directory / "supervision-start.json", canonical_json(value))
        return value

    # A live matching PID/start/boot identity cannot be finalized as abandoned.
    active = root / "active-structural-control"
    active_request = request(active)
    publish_new(active / "worker-started.json", canonical_json({"schema": "E0WorkerStartedV2",
        "request_version": digest(active_request), "process": _process_identity(os.getpid()),
        "resource_limits": _E0_LIMITS}))
    with test.assertRaisesRegex(ContractError, "still active"):
        _recover_e0(active)
    test.assertFalse((active / "supervision-finish.json").exists())
    acknowledgment = active / "worker-started.json"
    actual_acknowledgment = acknowledgment.read_bytes()
    changed_acknowledgment = json.loads(actual_acknowledgment)
    changed_acknowledgment["resource_limits"]["cpu_hard_seconds"] = 191
    acknowledgment.write_bytes(canonical_json(changed_acknowledgment))
    try:
        with test.assertRaisesRegex(IntegrityError, "another OS resource contract"):
            _recover_e0(active)
    finally:
        acknowledgment.write_bytes(actual_acknowledgment)

    abandoned = root / "abandoned-structural-control"
    request(abandoned)
    registry = TrialRegistry(abandoned / "trials")
    registry.register_family("INT10-supervision-structure", scope_ids=("V08",),
        protocol={"role": "registered_INT10_metadata_control_no_worker"}, max_attempts=1, cpu_budget_seconds=180)
    trial = registry.register(name="INT10-supervision-abandonment", family="INT10-supervision-structure",
        stage="integration", configuration={"control": "no_candidate_execution"}, code_hash=digest("control-code"),
        data_hashes={"input": digest("control-input")}, fold_version=digest("control-fold"), target_version="control")
    attempt = registry.start(trial, cpu_reservation_seconds=180)
    recovered = _recover_e0(abandoned)
    test.assertFalse(recovered["success"])
    receipt = recovered["supervision"]
    test.assertEqual((receipt["status"], receipt["charged_cpu_seconds"], receipt["resource_basis"]),
                     ("interrupted", 180, "reservation_charged_usage_unknown"))
    state = registry.state()
    test.assertEqual(len(state["attempts"]), 1)
    test.assertEqual(state["attempts"][attempt]["status"], "interrupted")
    test.assertEqual(state["attempts"][attempt]["cpu_seconds"], 180)
    test.assertFalse(state["attempts"][attempt]["result_artifacts"])
    preserved = (abandoned / "supervision-finish.json").read_bytes()
    history = registry.history()
    test.assertEqual(_recover_e0(abandoned), recovered)
    test.assertEqual(registry.history(), history)
    test.assertEqual((abandoned / "supervision-finish.json").read_bytes(), preserved)
    test.assertFalse((abandoned / "worker-started.json").exists())
    output = io.StringIO()
    with redirect_stdout(output):
        test.assertEqual(main(["e0-recover", "--output-root", str(abandoned)]), 1)
    test.assertEqual(json.loads(output.getvalue()), recovered)
    invalid = root / "invalid-observation-structural-control"
    request(invalid)
    with test.assertRaises(ContractError):
        _finalize_e0_supervision(invalid, exit_code=0, cpu_seconds=float("nan"), wall_seconds=1.,
            peak_rss_bytes=1024, reason="structural invalid-observation control", observed=True)
    test.assertFalse((invalid / "supervision-finish.json").exists())
