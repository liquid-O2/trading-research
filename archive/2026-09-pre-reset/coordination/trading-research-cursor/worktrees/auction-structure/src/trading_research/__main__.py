"""Implementation scope commands and bounded, retained E0 simulation commands."""

from contextlib import contextmanager
import argparse
import json
import math
from pathlib import Path
import stat

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.ledger import Ledger
from trading_research.operations.scope import Scope

ROOT = Path(__file__).resolve().parents[2]
_E0_LIMITS = {"cpu_soft_seconds": 180, "cpu_hard_seconds": 190,
              "address_space_bytes": 4 * 1024 ** 3, "wall_seconds_limit": 360}


def _e0_root(value):
    root = Path(value).absolute()
    for path in (root, *root.parents):
        if path.is_symlink():
            raise ContractError("E0 lifecycle cannot traverse symbolic links")
    return root


def _e0_json(root, name, *, limit=1024 * 1024):
    from trading_research.operations.artifacts import canonical_json
    path = root / name
    mode = path.lstat()
    if not stat.S_ISREG(mode.st_mode) or mode.st_size > limit:
        raise IntegrityError("E0 lifecycle requires bounded regular retained files")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    value = json.loads(raw)
    if len(raw) != mode.st_size or canonical_json(value) != raw:
        raise IntegrityError("E0 lifecycle bytes changed or are not canonical")
    return value


@contextmanager
def _e0_lock(root, name, *, blocking=False):
    import fcntl
    path = root / name
    if path.is_symlink():
        raise IntegrityError("E0 lifecycle lock cannot be a symbolic link")
    with path.open("a+b") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        except BlockingIOError as exc:
            raise ContractError("E0 lifecycle is already owned by another supervisor") from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _process_record(pid):
    if type(pid) is not int or pid <= 0:
        raise IntegrityError("E0 process identity requires a positive PID")
    try:
        tail = Path("/proc", str(pid), "stat").read_text().rsplit(")", 1)[1].split()
    except FileNotFoundError:
        return None
    return {"pid": pid, "start_ticks": int(tail[19]),
            "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip()}, tail[0]


def _process_identity(pid):
    record = _process_record(pid)
    return None if record is None else record[0]


def _process_alive(identity):
    if type(identity) is not dict or set(identity) != {"pid", "start_ticks", "boot_id"}:
        raise IntegrityError("E0 retained process identity is malformed")
    record = _process_record(identity["pid"])
    return record is not None and record[0] == identity and record[1] != "Z"


def _e0_launch_records(root, request, *, require_complete):
    from trading_research.operations.artifacts import digest
    records = {}
    for name, schema in (("supervision-launched.json", "E0SupervisionLaunchV2"),
                         ("worker-started.json", "E0WorkerStartedV2")):
        if not (root / name).exists():
            if require_complete:
                raise IntegrityError("E0 successful worker lacks actual launch/enforcement acknowledgment")
            continue
        record = _e0_json(root, name, limit=16384)
        expected = {"schema", "request_version", "process"}
        if name == "worker-started.json":
            expected.add("resource_limits")
        if (type(record) is not dict or set(record) != expected or record["schema"] != schema
                or record["request_version"] != digest(request)):
            raise IntegrityError("E0 launch/enforcement acknowledgment differs from its request")
        identity = record["process"]
        if identity is None:
            if require_complete or name == "worker-started.json":
                raise IntegrityError("E0 actual worker identity is missing")
        elif (type(identity) is not dict or set(identity) != {"pid", "start_ticks", "boot_id"}
                or type(identity["pid"]) is not int or identity["pid"] <= 0
                or type(identity["start_ticks"]) is not int or identity["start_ticks"] < 0
                or type(identity["boot_id"]) is not str or not identity["boot_id"]):
            raise IntegrityError("E0 worker process identity is malformed")
        if name == "worker-started.json":
            limits = record["resource_limits"]
            if (type(limits) is not dict or set(limits) != set(_E0_LIMITS)
                    or any(type(limits[key]) is not int or limits[key] != value for key, value in _E0_LIMITS.items())):
                raise IntegrityError("E0 worker enforced another OS resource contract")
        records[name] = record
    if (len(records) == 2 and records["supervision-launched.json"]["process"]
            != records["worker-started.json"]["process"]):
        raise IntegrityError("E0 supervisor and worker retain different process identities")
    return records


def _e0_request(root):
    request = _e0_json(root, "supervision-start.json", limit=16384)
    expected = {"schema", "status", "bundle", "output_root", "started_at_utc_ns", "supervisor",
                "maximum_physical_workers", "maximum_logical_runs", *_E0_LIMITS}
    if (type(request) is not dict or set(request) != expected or request["schema"] != "E0SupervisionV2"
            or request["status"] != "started" or request["output_root"] != str(root)
            or type(request["bundle"]) is not str or not Path(request["bundle"]).is_absolute()
            or type(request["started_at_utc_ns"]) is not int or request["started_at_utc_ns"] <= 0
            or type(request["maximum_physical_workers"]) is not int or request["maximum_physical_workers"] != 1
            or type(request["maximum_logical_runs"]) is not int or request["maximum_logical_runs"] != 64
            or any(type(request[key]) is not int or request[key] != value for key, value in _E0_LIMITS.items())):
        raise IntegrityError("E0 supervisor request differs from its exact bounded contract")
    return request


def _e0_resource_error(cpu_seconds, wall_seconds, peak_rss_bytes):
    """Strict final acceptance is separate from the kernel's stop thresholds."""
    for name, value, limit in (("cpu_seconds", cpu_seconds, 180), ("wall_seconds", wall_seconds, 360)):
        if (type(value) not in (int, float) or not 0 < value < limit
                or type(value) is float and not math.isfinite(value)):
            return name + " must be finite, positive and strictly below " + str(limit)
    if type(peak_rss_bytes) is not int or not 0 < peak_rss_bytes < 4 * 1024 ** 3:
        return "peak_rss_bytes must be an integer strictly between zero and 4 GiB"
    return None


def _matrix_summary(root):
    """Read one actual matrix artifact and join it to its registered trial."""
    from trading_research.operations.artifacts import artifact_ref, digest
    from trading_research.operations.trials import TrialRegistry
    from trading_research.experiments.e0.runner import load_e0_result_labels
    if not (root / "trials").is_dir() or (root / "trials").is_symlink():
        raise ContractError("no retained E0 trial registry")
    registry = TrialRegistry(root / "trials")
    state = registry.state()
    completed = []
    for attempt in state["attempts"].values():
        for reference in attempt.get("result_artifacts", ()):
            if reference["kind"] != "E0_complete_matrix" or attempt["status"] != "succeeded":
                continue
            ref = artifact_ref(reference)
            if ref.size_bytes > 64 * 1024 * 1024:
                raise IntegrityError("E0 matrix artifact exceeds its read bound")
            artifact_root = _e0_root(registry.artifacts.root / ref.sha256[:2])
            output = _e0_json(artifact_root, ref.sha256, limit=ref.size_bytes)
            if digest(output) != ref.sha256:
                raise IntegrityError("retained E0 matrix artifact hash changed")
            manifest = output["manifest"]
            trial = state["trials"][attempt["trial_id"]]
            version = digest(manifest)
            if (type(manifest["branches"]) is not list or len(manifest["branches"]) != 4
                    or type(manifest["target_multiples"]) is not list or len(manifest["target_multiples"]) != 2
                    or type(manifest["scenarios"]) is not list or len(manifest["scenarios"]) != 8
                    or type(output["results"]) is not list or len(output["results"]) != 64
                    or type(output["trials"]) is not list or len(output["trials"]) != 64):
                raise IntegrityError("retained E0 matrix changed its finite declared dimensions")
            expected_runs = {(branch, multiple, scenario["id"]) for branch in manifest["branches"]
                             for multiple in manifest["target_multiples"] for scenario in manifest["scenarios"]}
            scenario_versions = {scenario["id"]: digest(scenario) for scenario in manifest["scenarios"]}
            actual_runs = {(row["branch"], row["target_multiple"], row["scenario"]) for row in output["results"]}
            if (output["physical_attempt"] != attempt["id"] or len(output["results"]) != 64
                    or len(expected_runs) != 64 or actual_runs != expected_runs
                    or trial["configuration"]["manifest"] != version
                    or trial["code_hash"] != manifest["code_hash"]
                    or trial["fold_version"] != manifest["fold_version"]
                    or trial["data_hashes"] != dict(manifest["source_hashes"])
                    or trial["configuration"]["logical_trials"] != output["trials"]
                    or any(row["manifest_version"] != version
                           or row["scenario_version"] != scenario_versions[row["scenario"]]
                           for row in output["results"])):
                raise IntegrityError("retained E0 matrix differs from its actual registered attempt")
            references = output.get("label_inventory_artifacts")
            if (type(references) is not list or not 0 < len(references) <= 16
                    or len({ref["sha256"] for ref in references}) != len(references)):
                raise IntegrityError("retained E0 matrix lacks its finite label artifact inventory")
            declared = {ref["sha256"]: ref for ref in references}
            loaded = {}
            for row in output["results"]:
                ref = row.get("label_inventory_artifact", {})
                if declared.get(ref.get("sha256")) != ref:
                    raise IntegrityError("E0 result names an undeclared complete label artifact")
                if ref["sha256"] not in loaded:
                    loaded[ref["sha256"]] = load_e0_result_labels(registry.artifacts, row)
                labels = loaded[ref["sha256"]]
                if (labels["population_hash"] != row["population_hash"]
                        or labels["target_multiple"] != row["target_multiple"]
                        or labels["scenario_version"] != row["scenario_version"]
                        or labels["source_path_versions"] != row["source_path_versions"]
                        or labels["counts"]["population"] != row["population_count"]):
                    raise IntegrityError("E0 paired result changed its label population, policy, scenario or source")
            if set(loaded) != set(declared):
                raise IntegrityError("E0 matrix retains an unused label artifact")
            completed.append((attempt, reference, output))
    if len(completed) != 1:
        raise ContractError("no single successful retained complete E0 matrix")
    attempt, reference, output = completed[0]
    return {"success": True, "scope": output["manifest"]["scope"],
            "manifest_id": output["manifest"]["id"], "manifest_version": digest(output["manifest"]),
            "logical_runs": 64, "physical_attempt": attempt["id"], "matrix_artifact": reference,
            "matrix_resources": {key: attempt[key] for key in ("cpu_seconds", "wall_seconds", "peak_rss_bytes")},
            "market_evidence": output["market_evidence"], "program_complete": output["program_complete"],
            "historical_role": output["historical_role"]}


def _join_e0_supervision(receipt, matrix_summary):
    """Join physical OS observations to the exact successful inner artifact."""
    if receipt.get("status") != "succeeded" or type(receipt.get("exit_code")) is not int or receipt["exit_code"] != 0:
        raise IntegrityError("E0 successful report requires a successful observed worker")
    if receipt.get("resource_basis") != "observed_wait4":
        raise IntegrityError("E0 success cannot use estimated or reservation-only worker resources")
    error = _e0_resource_error(*(receipt.get(key) for key in ("cpu_seconds", "wall_seconds", "peak_rss_bytes")))
    if error:
        raise IntegrityError(error)
    if (receipt.get("matrix_artifact") != matrix_summary["matrix_artifact"]
            or receipt.get("physical_attempt") != matrix_summary["physical_attempt"]
            or receipt.get("manifest_version") != matrix_summary["manifest_version"]):
        raise IntegrityError("E0 supervisor and inner matrix identify different retained executions")
    inner = matrix_summary["matrix_resources"]
    error = _e0_resource_error(*(inner.get(key) for key in ("cpu_seconds", "wall_seconds", "peak_rss_bytes")))
    if error or any(inner[key] > receipt[key] for key in inner):
        raise IntegrityError("E0 inner measurement exceeds physical worker observations or its bound")
    return {**matrix_summary, "physical_resources": {key: receipt[key] for key in inner},
            "resource_basis": "observed_wait4", "physical_resources_accepted": True}


def _finalize_e0_supervision(root, *, exit_code, cpu_seconds, wall_seconds, peak_rss_bytes,
                             reason, observed):
    """Finalize an owned stopped lifecycle; never starts or reruns a worker."""
    from trading_research.operations.artifacts import canonical_json, digest, publish_new
    from trading_research.operations.trials import TrialRegistry
    root = _e0_root(root)
    request = _e0_request(root)
    if (root / "supervision-finish.json").exists():
        receipt = _e0_json(root, "supervision-finish.json")
        if receipt.get("request_version") != digest(request):
            raise IntegrityError("E0 completion belongs to another supervisor request")
        return receipt
    if type(observed) is not bool or type(reason) is not str or not reason:
        raise ContractError("E0 finalization requires explicit observed-resource basis and reason")
    if exit_code is not None and type(exit_code) is not int:
        raise ContractError("E0 worker exit code must be an integer or unknown")
    if observed and type(exit_code) is not int:
        raise ContractError("actual wait4 observations require the actual worker exit code")
    # Failed observations may be zero (launch failure) but cannot be nonfinite,
    # negative or mislabeled as actual wait4 usage.
    if observed:
        for value in (cpu_seconds, wall_seconds):
            if (type(value) not in (int, float) or value < 0
                    or type(value) is float and not math.isfinite(value)):
                raise ContractError("invalid actual E0 resource observation")
        if type(peak_rss_bytes) is not int or peak_rss_bytes < 0:
            raise ContractError("invalid actual E0 RSS observation")
    elif any(value is not None for value in (cpu_seconds, wall_seconds, peak_rss_bytes)):
        raise ContractError("unobserved E0 recovery cannot manufacture process measurements")
    error = _e0_resource_error(cpu_seconds, wall_seconds, peak_rss_bytes)
    status = ("succeeded" if observed and exit_code == 0 and error is None else
              "interrupted" if not observed or exit_code < 0 else "failed")
    if observed and exit_code == 0 and error:
        reason = "E0 physical resource acceptance failed: " + error
    receipt = {"schema": "E0SupervisionFinishV2", "request_version": digest(request),
               "status": status, "reason": reason, "exit_code": exit_code,
               "cpu_seconds": cpu_seconds, "wall_seconds": wall_seconds, "peak_rss_bytes": peak_rss_bytes,
               "resource_basis": "observed_wait4" if observed else "reservation_charged_usage_unknown",
               "charged_cpu_seconds": cpu_seconds if observed else request["cpu_soft_seconds"],
               "physical_attempt": None, "matrix_artifact": None, "manifest_version": None,
               "launch_version": None, "worker_started_version": None}
    if status == "succeeded":
        try:
            records = _e0_launch_records(root, request, require_complete=True)
            receipt.update(launch_version=digest(records["supervision-launched.json"]),
                           worker_started_version=digest(records["worker-started.json"]))
            matrix = _matrix_summary(root)
            receipt.update({key: matrix[key] for key in ("physical_attempt", "matrix_artifact", "manifest_version")})
            _join_e0_supervision(receipt, matrix)
        except (ContractError, IntegrityError, OSError, ValueError, TypeError, KeyError) as exc:
            receipt.update(status="failed", reason="E0 retained worker/matrix join failed: " + str(exc))
    # Write terminal evidence before closing pending inner attempts. Recovery
    # can replay the idempotent cleanup if the supervisor dies between steps.
    publish_new(root / "supervision-finish.json", canonical_json(receipt))
    _close_e0_running_attempts(root, receipt)
    return receipt


def _close_e0_running_attempts(root, receipt):
    from trading_research.operations.trials import TrialRegistry
    if not (root / "trials").is_dir():
        return
    registry = TrialRegistry(root / "trials")
    for identity, attempt in registry.state()["attempts"].items():
        if attempt["status"] == "running":
            registry.finish(identity, status="interrupted", cpu_seconds=receipt["cpu_seconds"],
                wall_seconds=receipt["wall_seconds"], peak_rss_bytes=receipt["peak_rss_bytes"], reason=receipt["reason"])


def _worker(bundle, output_root):
    import os
    import resource
    import signal
    from trading_research.operations.artifacts import canonical_json, digest, publish_new
    resource.setrlimit(resource.RLIMIT_CPU, (180, 190))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 ** 3, 4 * 1024 ** 3))
    signal.alarm(360)
    root = _e0_root(output_root)
    # The dispatch lock closes the parent-death/Popen/PID-publication window:
    # recovery either sees this acknowledgment or finalizes before any load.
    with _e0_lock(root, "dispatch.lock", blocking=True):
        request = _e0_request(root)
        if (request["bundle"] != str(Path(bundle).absolute()) or (root / "supervision-finish.json").exists()
                or (root / "worker-started.json").exists()):
            raise ContractError("internal E0 worker differs from its unused supervisor request")
        if (resource.getrlimit(resource.RLIMIT_CPU) != (180, 190)
                or resource.getrlimit(resource.RLIMIT_AS) != (4 * 1024 ** 3, 4 * 1024 ** 3)):
            raise ContractError("actual E0 OS limits differ from the retained request")
        publish_new(root / "worker-started.json", canonical_json({"schema": "E0WorkerStartedV2",
            "request_version": digest(request), "process": _process_identity(os.getpid()),
            "resource_limits": _E0_LIMITS}))
    from trading_research.experiments.e0.bundle import load_e0_bundle
    from trading_research.experiments.e0.runner import run_e0_matrix
    manifest, days, router = load_e0_bundle(bundle)
    run_e0_matrix(root, manifest=manifest, days=days, predict=router)
    return {"success": True, "logical_runs": 64}


def _run(bundle, output_root):
    import os
    import signal
    import subprocess
    import sys
    import time
    from trading_research.operations.artifacts import canonical_json, digest, publish_new
    root = _e0_root(output_root)
    root.mkdir(parents=True, exist_ok=False)
    with _e0_lock(root, "supervision.lock"):
        request = {"schema": "E0SupervisionV2", "status": "started", "bundle": str(Path(bundle).absolute()),
                   "output_root": str(root), "started_at_utc_ns": time.time_ns(),
                   "supervisor": _process_identity(os.getpid()), **_E0_LIMITS,
                   "maximum_physical_workers": 1, "maximum_logical_runs": 64}
        publish_new(root / "supervision-start.json", canonical_json(request))
        started = time.monotonic()
        process = None
        usage = None
        reason = "worker launch failed"
        exit_code = None
        try:
            with (root / "worker-output.log").open("xb") as log:
                with _e0_lock(root, "dispatch.lock", blocking=True):
                    process = subprocess.Popen([sys.executable, "-m", "trading_research", "_e0-worker",
                        "--bundle", request["bundle"], "--output-root", str(root)],
                        stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
                    publish_new(root / "supervision-launched.json", canonical_json({"schema": "E0SupervisionLaunchV2",
                        "request_version": digest(request), "process": _process_identity(process.pid)}))
                while True:
                    pid, wait_status, observed_usage = os.wait4(process.pid, os.WNOHANG)
                    if pid:
                        usage = observed_usage
                        exit_code = os.waitstatus_to_exitcode(wait_status)
                        process.returncode = exit_code
                        reason = "bounded E0 worker completed" if exit_code == 0 else "bounded E0 worker exited " + str(exit_code)
                        break
                    if time.monotonic() - started >= 360:
                        reason = "E0 worker exceeded 360 second wall bound"
                        break
                    time.sleep(.05)
        except KeyboardInterrupt:
            reason = "E0 worker interrupted by caller"
        finally:
            if process is not None and process.returncode is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _, wait_status, usage = os.wait4(process.pid, 0)
                exit_code = os.waitstatus_to_exitcode(wait_status)
                process.returncode = exit_code
            _finalize_e0_supervision(root, exit_code=exit_code,
                cpu_seconds=None if usage is None else usage.ru_utime + usage.ru_stime,
                wall_seconds=None if usage is None else time.monotonic() - started,
                peak_rss_bytes=None if usage is None else usage.ru_maxrss * 1024,
                reason=reason, observed=usage is not None)
    return _report(root)


def _recover_e0(output_root):
    """Recover the same stopped lifecycle without starting or signaling a worker."""
    from trading_research.operations.artifacts import digest
    root = _e0_root(output_root)
    if not root.is_dir():
        raise ContractError("E0 recovery requires its existing output directory")
    with _e0_lock(root, "supervision.lock"), _e0_lock(root, "dispatch.lock"):
        request = _e0_request(root)
        for record in _e0_launch_records(root, request, require_complete=False).values():
            if record["process"] is not None and _process_alive(record["process"]):
                raise ContractError("E0 worker is still active; recovery cannot finalize its execution")
        receipt = _finalize_e0_supervision(root, exit_code=None, cpu_seconds=None, wall_seconds=None,
            peak_rss_bytes=None, reason="recovered stopped E0 lifecycle; actual wait4 usage unavailable", observed=False)
        _close_e0_running_attempts(root, receipt)
    return _report(root)


def _report(output_root):
    from trading_research.operations.artifacts import digest
    root = _e0_root(output_root)
    if (root / "supervision-start.json").exists():
        request = _e0_request(root)
        if not (root / "supervision-finish.json").exists():
            return {"success": False, "status": "unfinished", "reason": "E0 lifecycle needs its stopped-worker finalization"}
        receipt = _e0_json(root, "supervision-finish.json")
        if receipt.get("request_version") != digest(request):
            raise IntegrityError("E0 final receipt belongs to another request")
        if receipt["status"] != "succeeded":
            return {"success": False, "supervision": receipt}
        records = _e0_launch_records(root, request, require_complete=True)
        if (receipt.get("launch_version") != digest(records["supervision-launched.json"])
                or receipt.get("worker_started_version") != digest(records["worker-started.json"])):
            raise IntegrityError("E0 launch/enforcement evidence changed after finalization")
        return _join_e0_supervision(receipt, _matrix_summary(root))
    # A matrix executed under the complete engineering-suite supervisor has its
    # own outer receipt. Do not relabel its inner interval as whole-worker CPU.
    return {**_matrix_summary(root), "physical_resources_accepted": False,
            "resource_basis": "matrix_interval_only_outer_supervision_not_supplied"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("import-scope", "audit", "e0-check", "e0-run", "e0-report", "e0-recover", "_e0-worker"))
    parser.add_argument("--plan-root", type=Path, default=ROOT.parent / "planning/trading-model")
    parser.add_argument("--ledger-root", type=Path, default=ROOT / "evidence")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command in ("e0-check", "e0-run", "_e0-worker") and args.bundle is None:
            raise ContractError("E0 command requires --bundle")
        if args.command in ("e0-run", "e0-report", "e0-recover", "_e0-worker") and args.output_root is None:
            raise ContractError("E0 execution/report/recovery requires --output-root")
        if args.command == "e0-check":
            from trading_research.experiments.e0.bundle import check_e0_bundle
            result = check_e0_bundle(args.bundle)
        elif args.command == "e0-run":
            result = _run(args.bundle, args.output_root)
        elif args.command == "_e0-worker":
            result = _worker(args.bundle, args.output_root)
        elif args.command == "e0-report":
            result = _report(args.output_root)
        elif args.command == "e0-recover":
            result = _recover_e0(args.output_root)
        else:
            scope = Scope.load(args.plan_root)
            ledger = Ledger(args.ledger_root)
            result = ledger.import_scope(scope) if args.command == "import-scope" else ledger.audit(scope, require_complete=args.require_complete)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("success", True) else 1
    except (ContractError, IntegrityError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"success": False, "error": type(exc).__name__, "reason": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
