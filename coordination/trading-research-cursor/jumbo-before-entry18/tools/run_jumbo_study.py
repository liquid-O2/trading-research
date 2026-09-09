"""Register and supervise one bounded research check or actual study attempt.

The parent imports only the existing artifact/trial infrastructure. Candidate
imports, tests, Arrow scans and fits happen after worker resource limits.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback

try:
    from .jumbo_resources import (amended_protocol, worker_limits, require_approved_execution_resources,
        apply_hardware_execution, live_hardware_limits, HARDWARE_MAXIMUM_MEMORY_BYTES)
    from .jumbo_verification import (authenticate_descriptive_confirmation, confirmation_feasibility,
                                     descriptive_confirmation_from_predecessor)
except ImportError:  # Direct CLI invocation places tools on sys.path.
    from jumbo_resources import (amended_protocol, worker_limits, require_approved_execution_resources,
        apply_hardware_execution, live_hardware_limits, HARDWARE_MAXIMUM_MEMORY_BYTES)
    from jumbo_verification import (authenticate_descriptive_confirmation, confirmation_feasibility,
                                    descriptive_confirmation_from_predecessor)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "validation/JUMBO_ACQUIRED_CONTRACT_STUDY_V1.json"
ANALYSIS_PLAN = ROOT / "validation/JUMBO_ANALYSIS_V1.json"
EXECUTION_PLAN = ROOT / "validation/JUMBO_EXECUTION_V11.json"
MODEL_PLAN = ROOT / "validation/JUMBO_MODELS_V1.json"
HARDWARE_EXECUTION = ROOT / "validation/JUMBO_HARDWARE_EXECUTION_V1.json"
MODES = ("check", "pilot", "admit", "develop", "confirm")
CHECK_TEST_SELECTION = [
    "tests.test_ohlc_ranges", "tests.test_ohlc_admission",
    "tests.test_ohlc_mechanisms", "tests.test_date_statistics",
    "tests.test_jumbo_tables", "tests.test_jumbo_report", "tests.test_jumbo_narrative",
    "tests.test_jumbo_anchors", "tests.test_jumbo_definition_supersession",
    "tests.test_jumbo_matrix", "tests.test_jumbo_targets", "tests.test_jumbo_baselines",
    "tests.test_jumbo_models", "tests.test_jumbo_model_backend",
    "tests.test_jumbo_model_evaluation", "tests.test_jumbo_evaluation_storage", "tests.test_jumbo_clock_comparison",
    "tests.test_jumbo_special_targets", "tests.test_jumbo_special_models", "tests.test_jumbo_locations",
    "tests.test_jumbo_location_tables", "tests.test_jumbo_location_models",
    "tests.test_jumbo_fitting", "tests.test_jumbo_verification", "tests.test_jumbo_descriptive_confirmation",
    "tests.test_trial_budget_amendment", "tests.test_research.LabelTests", "tests.test_research.TrialTests", "tests.test_v01_v02",
]


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def accounted_worker_report(report, maximum_output_bytes):
    """Close a declared research output budget over both report publications.

    Worker disk JSON is indented; the supervisor's ArtifactStore.put_json copy
    is canonical JSON. Each byte count includes its own serialized fields.
    Check/admission reports without a derived-output counter keep their schema.
    """
    if "derived_output_bytes" not in report:
        return report, encoded(report)
    from trading_research.operations.artifacts import canonical_json
    original = report["derived_output_bytes"]
    if (type(original) is not int or original < 0
            or type(maximum_output_bytes) is not int or maximum_output_bytes < 0):
        raise ValueError("exact nonnegative aggregate output byte counts required")
    result = dict(report)
    result.update(derived_output_before_worker_report_bytes=original,
                  worker_report_disk_bytes=0, worker_report_cas_bytes=0)
    for _ in range(32):
        disk = encoded(result)
        disk_bytes, cas_bytes = len(disk), len(canonical_json(result))
        total = original + disk_bytes + cas_bytes
        if (result["worker_report_disk_bytes"] == disk_bytes
                and result["worker_report_cas_bytes"] == cas_bytes
                and result["derived_output_bytes"] == total):
            if total > maximum_output_bytes:
                raise ValueError("worker disk and CAS reports exceed aggregate derived-output allowance before publication")
            return result, disk
        result.update(worker_report_disk_bytes=disk_bytes,
                      worker_report_cas_bytes=cas_bytes, derived_output_bytes=total)
    raise ValueError("worker report byte accounting did not reach stable serialization")


def checked(path, expected=None, maximum=16 * 1024 * 1024):
    path = Path(path)
    if "archive" in path.parts or not path.is_file() or path.stat().st_size > maximum:
        raise ValueError("bounded retained file required")
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if expected and sha != expected:
        raise ValueError(f"frozen file changed: {path}")
    return raw, sha


def resource_document(reference):
    path = (ROOT / reference["path"]).resolve()
    if not path.is_relative_to(ROOT / "validation"):
        raise ValueError("resource approval must be a retained validation document")
    raw, _ = checked(path, reference["sha256"], maximum=128 * 1024)
    if len(raw) != reference["size_bytes"]:
        raise ValueError("resource authorization size changed")
    return raw


def execution_authorization(execution_plan, override_path=None):
    """Keep the frozen scientific/execution plan while recording current approval."""
    reference = execution_plan["resource_amendment"]
    baseline_raw = resource_document(reference)
    if override_path is None:
        current_raw = baseline_raw
    else:
        path = Path(override_path)
        path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_relative_to(ROOT / "validation"):
            raise ValueError("resource approval override must be inside retained validation")
        current_raw, sha = checked(path, maximum=128 * 1024)
        reference = {"path": str(path.relative_to(ROOT)), "sha256": sha, "size_bytes": len(current_raw)}
    require_approved_execution_resources(json.loads(baseline_raw), json.loads(current_raw), execution_plan)
    return reference, current_raw


def hardware_execution(protocol, budget_reference, reference=None):
    if reference is None:
        raw, sha = checked(HARDWARE_EXECUTION, maximum=128 * 1024)
        reference = {'path': str(HARDWARE_EXECUTION.relative_to(ROOT)),
                     'sha256': sha, 'size_bytes': len(raw)}
    else:
        raw = resource_document(reference)
    allocation = json.loads(raw)
    resource_document(allocation['hardware_specification'])
    live = live_hardware_limits()
    effective = apply_hardware_execution(protocol, allocation,
                     budget_reference=budget_reference, live_limits=live)
    return reference, effective, live


def worker(packet_path):
    # Fixed bootstrap caps apply even to malformed direct invocations. Tighter
    # registered mode limits replace these before imports or observations.
    resource.setrlimit(resource.RLIMIT_CPU, (10010, 10010))
    resource.setrlimit(resource.RLIMIT_AS, (HARDWARE_MAXIMUM_MEMORY_BYTES, HARDWARE_MAXIMUM_MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (536870912, 536870912))
    packet = json.loads(checked(packet_path, maximum=512 * 1024)[0])
    protocol = json.loads(checked(PROTOCOL, packet["protocol_sha256"], maximum=512 * 1024)[0])
    amendment_ref = packet["resource_amendment"]
    amendment_raw = resource_document(amendment_ref)
    frozen_execution = json.loads(checked(EXECUTION_PLAN, packet["execution_plan"]["sha256"])[0])
    baseline_authorization = json.loads(resource_document(frozen_execution["resource_amendment"]))
    require_approved_execution_resources(baseline_authorization, json.loads(amendment_raw), frozen_execution)
    protocol = amended_protocol(protocol, packet["protocol_sha256"], json.loads(amendment_raw))
    _, protocol, observed_hardware = hardware_execution(protocol, amendment_ref, packet['hardware_execution'])
    limits = packet["limits"]
    if limits != worker_limits(protocol, packet["phase"]):
        raise ValueError("worker limits differ from the explicitly authorized resource amendment")
    resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"], limits["hard_cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (limits["memory_bytes"], limits["memory_bytes"]))
    file_limit = min(limits['maximum_output_bytes'], 512 * 1024 * 1024)
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
    try:
        from trading_research.operations.artifacts import artifact_ref
        from trading_research.operations.trials import TrialRegistry
        registry = TrialRegistry(ROOT / "evidence/trials")
        state = registry.state()
        attempt = state["attempts"][packet["attempt_id"]]
        trial = state["trials"][packet["trial_id"]]
        if (attempt["status"] != "running" or attempt["trial_id"] != packet["trial_id"]
                or attempt["family"] != protocol["family"] or trial["code_hash"] != packet["code_snapshot"]["sha256"]
                or trial["configuration"]["mode"] != packet["mode"]
                or trial["configuration"]["protocol_sha256"] != packet["protocol_sha256"]
                or trial["configuration"]["tools_snapshot"] != packet["tools_snapshot"]
                or trial["configuration"]["predecessor"] != packet["predecessor"]
                or trial["configuration"]["phase"] != packet["phase"]
                or trial["configuration"]["analysis_plan"] != packet["analysis_plan"]
                or trial["configuration"]["execution_plan"] != packet["execution_plan"]
                or trial["configuration"]["model_plan"] != packet["model_plan"]
                or trial["configuration"]["resource_amendment"] != packet["resource_amendment"]
                or trial["configuration"]["hardware_execution"] != packet["hardware_execution"]
                or trial["configuration"]["verification_contracts"] != packet["verification_contracts"]
                or trial["configuration"].get("descriptive_confirmation") != packet.get("descriptive_confirmation")
                or os.getppid() != packet["supervisor_pid"]
                or Path(packet_path).resolve() != ROOT / "reports/jumbo-runs" / packet["attempt_id"] / "packet.json"
                or Path(packet["worker_report"]) != Path(packet_path).parent / "worker.json"):
            raise ValueError("worker packet does not identify its active registered attempt and supervisor")
        if any(os.environ.get(name) != value for name, value in trial['configuration']['thread_limits'].items()):
            raise ValueError('worker native thread settings differ from registered execution')
        authorization = json.loads(amendment_raw)
        recorded = state["budget_amendments"].get(authorization["amendment_id"])
        if (recorded is None or recorded["payload"]["authorization"]["sha256"] != amendment_ref["sha256"]
                or state["effective_budgets"][protocol["family"]] != authorization["authorized_limits"]
                or attempt["cpu_reservation_seconds"] != limits["hard_cpu_seconds"]):
            raise ValueError("worker authorization is not the current appended family budget")
        actual_manifest = registry.artifacts.read_json(artifact_ref(packet["code_snapshot"]))["manifest"]
        tool_files = registry.artifacts.read_json(artifact_ref(packet["tools_snapshot"]))
        actual_manifest.update({name: value["sha256"] for name, value in tool_files.items()})
        if actual_manifest != packet["code_manifest"]:
            raise ValueError("worker manifest differs from retained registered code")
        # Validate the exact tested source snapshot before candidate imports.
        for name, sha in packet["code_manifest"].items():
            checked(ROOT / name, sha)
        checked(ANALYSIS_PLAN, packet["analysis_plan"]["sha256"])
        checked(EXECUTION_PLAN, packet["execution_plan"]["sha256"])
        checked(MODEL_PLAN, packet["model_plan"]["sha256"])
        plan = registry.artifacts.read_json(artifact_ref(packet["analysis_plan"]))
        execution_plan = registry.artifacts.read_json(artifact_ref(packet["execution_plan"]))
        for ref in (execution_plan["reference_manifest"], execution_plan["interrupted_attempt_review"],
                    *execution_plan["completed_shards"], execution_plan["prior_reference_check"],
                    execution_plan['previous_execution_plan'], execution_plan['consolidated_check_failure_review'],
                    *execution_plan.get('additional_supporting_inputs', ())):
            raw, _ = checked(ROOT / ref["path"], ref["sha256"])
            if len(raw) != ref["size_bytes"]:
                raise ValueError("execution supporting-input size differs")
        for ref in plan["supporting_inputs"]:
            raw, _ = checked(ROOT / ref["path"], ref["sha256"])
            if len(raw) != ref["size_bytes"]:
                raise ValueError("analysis supporting-input size differs")
        from importlib.metadata import version
        runtime_versions = {name: version(name) for name in plan["runtime_versions"]}
        if runtime_versions != plan["runtime_versions"]:
            raise ValueError("research runtime differs from its pinned providers")
        predecessor_execution = None
        if packet.get("predecessor"):
            predecessor_execution = json.loads(checked(
                ROOT / packet["predecessor"]["path"], packet["predecessor"]["sha256"])[0])
        authenticate_descriptive_confirmation(
            packet.get("descriptive_confirmation") is True, predecessor_execution,
            configured=trial["configuration"].get("descriptive_confirmation") is True, mode=packet['mode'])
        if packet["mode"] == "check":
            import unittest
            selected = CHECK_TEST_SELECTION
            suite = unittest.defaultTestLoader.loadTestsFromNames(selected)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            report = {"status": "passed" if result.wasSuccessful() else "failed",
                      "test_selection": selected, "tests": result.testsRun,
                      "failures": len(result.failures), "errors": len(result.errors),
                      "skipped": len(result.skipped), "actual_market_data_scans": 0,
                      "market_model_fits": 0,
                      "fixture_learning": "Selected numerical and orchestration tests fit synthetic fixtures, including freeze/restore; actual market resource probes are reported separately and make no quality claim."}
            success = result.wasSuccessful() and not result.skipped
            if success:
                from trading_research.research.jumbo_parity import check_actual_extraction
                parity = check_actual_extraction(packet, protocol, ROOT, registry.artifacts)
                report.update(actual_extraction_parity=parity,
                              actual_market_data_scans=parity.get('actual_market_data_read_attempts',parity["actual_admitted_tables_read"]),
                              market_model_fits=parity['market_model_fits'],
                              derived_output_bytes=parity.get('derived_output_bytes',0),
                              resource_probe_only=True)
                success = parity["passed"]
        else:
            from trading_research.research.jumbo_study import run
            report = run(packet, protocol, ROOT)
            success = report.get("success") is True
        report.update({"trial_id": packet["trial_id"], "attempt_id": packet["attempt_id"],
                       "protocol_sha256": packet["protocol_sha256"],
                       "code_snapshot": packet["code_snapshot"], "tools_snapshot": packet["tools_snapshot"],
                       "mode": packet["mode"], "success": success})
        report.update(phase=packet["phase"], analysis_plan=packet["analysis_plan"], resource_amendment=packet["resource_amendment"],
                      hardware_execution=packet['hardware_execution'], observed_hardware=observed_hardware,
                      execution_plan=packet["execution_plan"], model_plan=packet["model_plan"],
                      verification_contracts=packet["verification_contracts"], runtime_versions=runtime_versions,
                      descriptive_confirmation=packet.get("descriptive_confirmation") is True)
        from trading_research.operations.artifacts import publish_new
        report, report_payload = accounted_worker_report(report, limits["maximum_output_bytes"])
        publish_new(Path(packet["worker_report"]), report_payload)
        return 0 if success else 1
    except BaseException:
        traceback.print_exc()
        return 1


def parent(mode, parent_report=None, phase=None, resource_authorization=None):
    sys.path.insert(0, str(ROOT / "src"))
    from trading_research.operations.artifacts import artifact_ref, code_snapshot, publish_new, digest
    from trading_research.operations.trials import TrialRegistry
    raw, protocol_sha = checked(PROTOCOL)
    protocol = json.loads(raw)
    phase = phase or {"check": "code_check", "pilot": "admission_pilot", "admit": "full_admission",
                      "develop": "extract", "confirm": "confirmation"}[mode]
    if phase not in {"check": ("code_check",), "pilot": ("admission_pilot",), "admit": ("full_admission",),
                     "develop": ("extract", "fit"), "confirm": ("confirmation",)}[mode]:
        raise ValueError("unsupported declared mode/phase")
    original_limits = protocol["resources"]
    registry = TrialRegistry(ROOT / "evidence/trials")
    store = registry.artifacts
    analysis_raw, analysis_sha = checked(ANALYSIS_PLAN)
    analysis_ref = store.put_bytes(analysis_raw, kind="jumbo_analysis_plan_v1")
    execution_raw, _ = checked(EXECUTION_PLAN)
    execution_plan = json.loads(execution_raw)
    if (execution_plan["same_registered_family"] != protocol["family"]
            or execution_plan["analysis_plan_sha256"] != analysis_sha):
        raise ValueError("execution plan differs from its scientific family/analysis")
    execution_ref = store.put_bytes(execution_raw, kind="jumbo_execution_plan_v1")
    amendment_ref, amendment_raw = execution_authorization(execution_plan, resource_authorization)
    authorization_ref = store.put_bytes(amendment_raw, kind="family_budget_authorization_v1")
    protocol = amended_protocol(protocol, protocol_sha, json.loads(amendment_raw))
    hardware_ref, protocol, observed_hardware = hardware_execution(protocol, amendment_ref)
    store.put_bytes(resource_document(hardware_ref), kind='jumbo_user_hardware_execution_v1')
    limits = protocol["resources"]
    phase_limits = worker_limits(protocol, phase)
    model_raw, _ = checked(MODEL_PLAN)
    if json.loads(model_raw)["same_registered_family"] != protocol["family"]:
        raise ValueError("model plan changed the registered scientific family")
    model_ref = store.put_bytes(model_raw, kind="jumbo_model_plan_v1")
    for ref in (execution_plan["reference_manifest"], execution_plan["interrupted_attempt_review"],
                *execution_plan["completed_shards"], execution_plan["prior_reference_check"],
                execution_plan['previous_execution_plan'], execution_plan['consolidated_check_failure_review'],
                *execution_plan.get('additional_supporting_inputs', ())):
        payload, _ = checked(ROOT / ref["path"], ref["sha256"])
        if len(payload) != ref["size_bytes"]:
            raise ValueError("execution supporting-input size differs")
        store.put_bytes(payload, kind=ref.get("kind",'jumbo_execution_support_v1'))
    for ref in json.loads(analysis_raw)["supporting_inputs"]:
        raw_support, _ = checked(ROOT / ref["path"], ref["sha256"])
        if len(raw_support) != ref["size_bytes"]:
            raise ValueError("analysis supporting-input size differs")
        store.put_bytes(raw_support, kind=ref["kind"])
    # Small source metadata is pinned before registration; market values are
    # admitted and byte-hashed only inside the bounded data worker.
    refs = []
    for ref in protocol["frozen_metadata"]:
        payload, sha = checked(ROOT / ref["path"], ref["sha256"])
        if len(payload) != ref["size_bytes"]:
            raise ValueError("frozen metadata size mismatch")
        refs.append(asdict(store.put_bytes(payload, kind="research_study_metadata")))
    protocol_ref = store.put_bytes(raw, kind="research_study_protocol")
    registration = {"protocol": asdict(protocol_ref), "frozen_metadata": refs,
                    "active_scope": protocol["active_scope"], "question": protocol["question"]}
    registry.register_family(protocol["family"], scope_ids=("C01", "C02", "C03", "C04", "C05", "C06", "C21", "L01", "L02", "L03", "L04"),
                             protocol=registration, max_attempts=original_limits["maximum_attempts"],
                             cpu_budget_seconds=original_limits["cpu_budget_seconds"])
    registry.amend_budget(authorization=asdict(authorization_ref))
    snapshot = code_snapshot(ROOT, store)
    manifest = store.read_json(snapshot)["manifest"]
    tool_files = {}
    for tool_name in ("tools/run_jumbo_study.py", "tools/jumbo_verification.py", "tools/jumbo_resources.py"):
        tool_raw, tool_sha = checked(ROOT / tool_name)
        tool_files[tool_name] = {"sha256": tool_sha, "content_hex": tool_raw.hex()}
        manifest[tool_name] = tool_sha
    tool_snapshot = store.put_json(tool_files, kind="research_study_tools_snapshot")
    from jumbo_verification import phase_contracts
    contracts = phase_contracts(ROOT, manifest, analysis_plan=asdict(analysis_ref),
                 execution_plan=asdict(execution_ref), model_plan=asdict(model_ref),
                 runtime_versions=json.loads(analysis_raw)["runtime_versions"])
    predecessor = None
    state = registry.state()
    if parent_report:
        parent_path = Path(parent_report).resolve()
        if not parent_path.is_relative_to(ROOT / "reports"):
            raise ValueError("study predecessor must be a retained package report")
        parent_raw, parent_sha = checked(parent_path)
        predecessor = json.loads(parent_raw)
        if predecessor.get("family") != protocol["family"] or predecessor.get("success") is not True:
            raise ValueError("successful same-family predecessor required")
        past_attempt = state["attempts"].get(predecessor.get("attempt_id"))
        past_trial = state["trials"].get(predecessor.get("trial_id"))
        if (past_attempt is None or past_trial is None or past_attempt["status"] != "succeeded"
                or past_attempt["trial_id"] != predecessor["trial_id"] or past_attempt["family"] != protocol["family"]
                or predecessor["protocol_sha256"] != protocol_sha
                or past_trial["code_hash"] != predecessor["code_snapshot"]["sha256"]
                or past_trial["configuration"]["tools_snapshot"] != predecessor["tools_snapshot"]
                or not any(r["kind"] == "research_study_execution" and r["sha256"] == digest(predecessor)
                           for r in past_attempt["result_artifacts"])):
            raise ValueError("predecessor lacks its exact successful registered evidence receipt")
        parent_identity = {"path": str(parent_path.relative_to(ROOT)), "sha256": parent_sha}
    else:
        parent_identity = None
    required = ("develop" if mode == "develop" and phase == "fit" else
                {"pilot": "check", "admit": "pilot", "develop": "admit", "confirm": "develop"}.get(mode))
    if required and (predecessor is None or predecessor["mode"] != required):
        raise ValueError(f"{mode} requires the retained successful {required} report")
    if mode == "confirm":
        if predecessor.get("phase") not in ("extract", "fit"):
            raise ValueError("target-specific predecessor phase differs")
    elif phase == "fit":
        if predecessor.get("phase") != "extract":
            raise ValueError("target-specific predecessor phase differs")
    descriptive_confirmation = authenticate_descriptive_confirmation(
        descriptive_confirmation_from_predecessor(predecessor, mode=mode), predecessor, mode=mode)
    if mode != "check":
        checks = [a for a in state["attempts"].values() if a["family"] == protocol["family"] and a["status"] == "succeeded"
                  and state["trials"][a["trial_id"]]["configuration"]["mode"] == "check"]
        verification_phase = phase if phase in ("extract", "fit", "confirmation") else "admission"
        matching_checks = [a for a in checks
                   if state["trials"][a["trial_id"]]["configuration"].get("verification_contracts", {}).get(verification_phase) == contracts[verification_phase]
                   and state["trials"][a["trial_id"]]["configuration"]["tools_snapshot"] == asdict(tool_snapshot)]
        if not matching_checks:
            raise ValueError("study mode requires a successful check of its exact relevant dependency, test, data/schema/spec and runtime contract")
        if phase in ('extract','fit','confirmation'):
            measured_feasible = False
            for past in matching_checks:
                for ref in past["result_artifacts"]:
                    if ref["kind"] == "research_study_execution":
                        check_execution = store.read_json(artifact_ref(ref))
                        check_worker = store.read_json(artifact_ref(check_execution["worker_report"]))
                        parity = check_worker.get("actual_extraction_parity", {})
                        if phase == 'confirmation' and descriptive_confirmation:
                            measured_feasible |= confirmation_feasibility(
                                parity, descriptive_confirmation=True,
                                cpu_cap_seconds=phase_limits['cpu_seconds'],
                                output_cap_bytes=phase_limits['maximum_output_bytes'])
                        else:
                            resource_result = parity if phase=='extract' else parity.get('model_preflight',{})
                            field = {'extract':'within_declared_extract_cap','fit':'within_declared_fit_cap',
                                     'confirmation':'within_declared_confirmation_cap'}[phase]
                            measured_feasible |= parity.get('passed') is True and resource_result.get(field) is True
            if not measured_feasible:
                raise ValueError(f"actual consolidated check does not establish {phase} feasibility within its unchanged CPU, memory and output caps")
    configuration = {"mode": mode, "protocol_sha256": protocol_sha,
                     "resource_amendment": amendment_ref,
                     "hardware_execution": hardware_ref, "observed_hardware": observed_hardware,
                     "phase": phase, "analysis_plan": asdict(analysis_ref), "execution_plan": asdict(execution_ref),
                     "model_plan": asdict(model_ref), "verification_contracts": contracts,
                     "tools_snapshot": asdict(tool_snapshot), "predecessor": parent_identity,
                     "descriptive_confirmation": descriptive_confirmation,
                     "python": sys.version, "executable": sys.executable,
                     "thread_limits": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "ARROW_NUM_THREADS": "1"}}
    trial = registry.register(name=f"{protocol['study_id']}:{mode}:{phase}", family=protocol["family"],
                              stage="engineering" if mode == "check" else "model" if mode in ("develop", "confirm") else "original",
                              configuration=configuration, code_hash=snapshot.sha256,
                              data_hashes={"protocol": protocol_sha}, fold_version="2020-2022_train_2023-2024_development_2025plus_heldout-v1",
                              target_version="observed-minute-ohlc-ranges-paths-v1",
                              parent_trial=None if predecessor is None else predecessor["trial_id"])
    cpu = phase_limits["cpu_seconds"]
    hard = phase_limits["hard_cpu_seconds"]
    attempt = registry.start(trial, cpu_reservation_seconds=hard)
    destination = ROOT / "reports/jumbo-runs" / attempt
    packet = {"mode": mode, "trial_id": trial, "attempt_id": attempt,
              "resource_amendment": amendment_ref,
              "hardware_execution": hardware_ref,
              "phase": phase, "analysis_plan": asdict(analysis_ref), "execution_plan": asdict(execution_ref),
                     "model_plan": asdict(model_ref), "verification_contracts": contracts,
              "protocol_sha256": protocol_sha, "code_snapshot": asdict(snapshot),
              "tools_snapshot": asdict(tool_snapshot), "code_manifest": manifest,
              "predecessor": parent_identity, "descriptive_confirmation": descriptive_confirmation,
              "worker_report": str(destination / "worker.json"), "supervisor_pid": os.getpid(),
              "limits": phase_limits}
    env = {**os.environ, **configuration["thread_limits"], "PYTHONHASHSEED": "0"}
    started = time.monotonic()
    observed = None
    timed_out = False
    process = None
    finalized = False
    try:
        destination.mkdir(parents=True, exist_ok=False)
        publish_new(destination / "packet.json", encoded(packet))
        with (destination / "worker.log").open("xb") as log:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker", str(destination / "packet.json")],
                                       cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            while True:
                pid, status, usage = os.wait4(process.pid, os.WNOHANG)
                if pid:
                    observed = usage
                    process.returncode = os.waitstatus_to_exitcode(status)
                    break
                if time.monotonic() - started > phase_limits["wall_seconds"]:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGKILL)
                    _, status, observed = os.wait4(process.pid, 0)
                    process.returncode = os.waitstatus_to_exitcode(status)
                    break
                time.sleep(0.2)
        worker_path = destination / "worker.json"
        worker_value = json.loads(checked(worker_path, maximum=limits["maximum_derived_output_bytes"])[0]) if worker_path.exists() else None
        joined = worker_value is not None and all(worker_value.get(k) == packet[k] for k in
                  ("trial_id", "attempt_id", "protocol_sha256", "code_snapshot", "tools_snapshot", "mode", "phase", "analysis_plan", "execution_plan", "model_plan", "verification_contracts", "resource_amendment", "hardware_execution", "descriptive_confirmation"))
        within_limits = (observed.ru_utime + observed.ru_stime <= cpu and observed.ru_maxrss * 1024 <= limits["memory_bytes"]
                         and time.monotonic() - started <= phase_limits["wall_seconds"] and not timed_out)
        success = bool(process.returncode == 0 and joined and within_limits and worker_value.get("success") is True)
        report = {"family": protocol["family"], "mode": mode, "trial_id": trial, "attempt_id": attempt,
                  "resource_amendment": amendment_ref, "limits": phase_limits,
                  "hardware_execution": hardware_ref, "observed_hardware": observed_hardware,
                  "phase": phase, "analysis_plan": asdict(analysis_ref), "execution_plan": asdict(execution_ref),
                     "model_plan": asdict(model_ref), "verification_contracts": contracts,
                  "success": success, "code_snapshot": asdict(snapshot), "tools_snapshot": asdict(tool_snapshot),
                  "protocol_sha256": protocol_sha, "predecessor": parent_identity,
                  "worker_report": None if worker_value is None else asdict(store.put_json(worker_value, kind="research_study_worker_report")),
                  "worker_report_path": str(worker_path.relative_to(ROOT)),
                  "worker_log": asdict(store.put_bytes(checked(destination / "worker.log", maximum=16 * 1024 * 1024)[0], kind="research_study_worker_log")),
                  "exit_code": process.returncode, "wall_timeout": timed_out,
                  "worker_identity_joined": joined, "within_declared_limits": within_limits,
                  "cpu_seconds": observed.ru_utime + observed.ru_stime, "wall_seconds": time.monotonic() - started,
                  "peak_rss_bytes": observed.ru_maxrss * 1024, "resource_basis": "wait4_specific_worker_and_descendants",
                  "economic_or_live_runs": 0, "finished_at": datetime.now(timezone.utc).isoformat()}
        report_ref = store.put_json(report, kind="research_study_execution")
        registry.finish(attempt, status="succeeded" if success else "failed", cpu_seconds=report["cpu_seconds"],
                        wall_seconds=report["wall_seconds"], peak_rss_bytes=report["peak_rss_bytes"],
                        reason="bounded worker report and observed completion" if success else "bounded worker failed; retained log and any partial artifacts",
                        result_artifacts=(asdict(report_ref),))
        finalized = True
        publish_new(destination / "execution.json", encoded(report))
        print(json.dumps({"report": str((destination / "execution.json").relative_to(ROOT)),
                          "success": success, "cpu_seconds": report["cpu_seconds"], "peak_rss_bytes": report["peak_rss_bytes"]}), flush=True)
        return 0 if success else 1
    except BaseException as exc:
        if process is not None and process.returncode is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
                _, status, observed = os.wait4(process.pid, 0)
                process.returncode = os.waitstatus_to_exitcode(status)
            except (ProcessLookupError, ChildProcessError):
                pass
        if not finalized:
            registry.finish(attempt, status="interrupted", cpu_seconds=0.0 if process is None else None if observed is None else observed.ru_utime + observed.ru_stime,
                            wall_seconds=time.monotonic() - started, peak_rss_bytes=0 if process is None else None if observed is None else observed.ru_maxrss * 1024,
                            reason=f"supervisor exception: {type(exc).__name__}; no worker launched" if process is None else
                                   f"supervisor exception: {type(exc).__name__}; prior reservation retained if usage unknown")
        raise


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        raise SystemExit(worker(sys.argv[2]))
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=MODES)
    parser.add_argument("predecessor", nargs="?")
    parser.add_argument("phase", nargs="?")
    parser.add_argument("--resource-authorization", help="Exact retained same-family approval within the execution envelope")
    args = parser.parse_args()
    raise SystemExit(parent(args.mode, args.predecessor, args.phase, args.resource_authorization))
