#!/usr/bin/env python3
"""Independent foundation acceptance probes. Never writes to implementation inputs.

Exit 0 requires valid controls AND rejection of every malformed case. Exit 1
means a behavioral mismatch; exit 2 means this harness could not run correctly.
The implementation agent must fix the implementation, not edit this checker.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p15-00", type=Path, required=True)
    parser.add_argument("--p15-01", type=Path, required=True)
    parser.add_argument("--subphase", type=Path, required=True)
    parser.add_argument("--graph", type=Path, default=ROOT / "planning/research-program/TASK_GRAPH.json")
    parser.add_argument("--output-root", type=Path, required=True, help="New directory; existing paths are refused")
    args = parser.parse_args()
    out = args.output_root.resolve()
    inputs = [args.p15_00.resolve(), args.p15_01.resolve(), args.subphase.resolve(), args.graph.resolve()]
    if out.exists() or any(path == out or out in path.parents for path in inputs):
        parser.error("output-root must be new and must not contain any input")
    out.mkdir(parents=True)
    records: list[dict] = []

    def write(name: str, value: object) -> Path:
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write("\n")
        return path

    def cli(name: str, mode: str, path: Path, *extra: str | Path, expected: int = 2) -> None:
        flag = "--manifest" if mode == "lineage" else "--receipt"
        command = [sys.executable, str(ROOT / "implementation/tools/verify_research_release.py"),
                   mode, flag, str(path)]
        if mode != "lineage":
            command += ["--graph", str(inputs[3])]
        command.extend(map(str, extra))
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=60)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = None
        structured = (isinstance(payload, dict) and payload.get("ok") is True) if expected == 0 else (
            isinstance(payload, list) and bool(payload) and all(
                isinstance(item, dict) and all(isinstance(item.get(key), str) and item[key]
                                              for key in ("code", "path", "detail")) for item in payload))
        records.append({"case": name, "kind": "cli", "expected_exit": expected,
                        "actual_exit": result.returncode, "passed": result.returncode == expected and structured,
                        "argv": command, "seconds": time.perf_counter() - start,
                        "stdout": result.stdout, "stderr": result.stderr})

    def mutation(name: str, change) -> None:
        doc = copy.deepcopy(p00)
        change(doc)
        cli(name, "task", write(name + ".json", doc))

    def rebind_child(doc: dict, parent_hash: str) -> dict:
        """Keep the child draft/run binding valid while substituting its parent.

        This independent JSON recipe avoids importing the verifier's own helpers.
        A failure must come from the predecessor, not an accidentally stale run ID.
        """
        doc["predecessor_receipts"]["P15-00"] = parent_hash
        entry = next(item for item in doc["artifact_manifest"] if Path(item["path"]).name == "DRAFT_MANIFEST.json")
        manifest = read(Path(entry["path"]))
        manifest["predecessor_receipts"] = copy.deepcopy(doc["predecessor_receipts"])
        path = write("child/DRAFT_MANIFEST.json", manifest)
        entry.update(path=str(path), sha256=sha(path), bytes=path.stat().st_size)
        doc["run_id"] = canonical_sha(manifest)[:16]
        return doc

    def constructor(name: str, build, expected: str) -> None:
        try:
            build()
            actual = "accepted"
            detail = ""
        except ContractError as exc:
            actual, detail = "ContractError", str(exc)
        except Exception as exc:
            actual, detail = "unexpected:" + type(exc).__name__, str(exc)
        records.append({"case": name, "kind": "constructor", "expected": expected,
                        "actual": actual, "passed": actual == expected, "detail": detail})

    try:
        initial_hashes = {str(path): sha(path) for path in inputs}
        p00, p01, subphase, graph = map(read, inputs)
        if p00.get("task_id") != "P15-00" or p01.get("task_id") != "P15-01" or subphase.get("subphase_id") != "00-foundation":
            raise ValueError("Supply actual P15-00, P15-01 and 00-foundation receipts")
        cli("valid_p15_00", "task", inputs[0], expected=0)
        cli("valid_p15_01", "task", inputs[1], expected=0)
        cli("valid_subphase", "subphase", inputs[2], expected=0)
        mutation("required_artifacts_omitted", lambda d: d.update(artifact_manifest=[]))
        mutation("required_baseline_binding_omitted", lambda d: d.update(artifact_manifest=[
            a for a in d["artifact_manifest"] if Path(a["path"]).name != "BASELINE_BINDING.json"]))
        for key, length in (("plan_sha256", 64), ("code_sha256", 64), ("run_id", 16)):
            mutation(key + "_replaced", lambda d, k=key, n=length: d.update({k: "0" * n}))
        mutation("non_hex_plan_identity", lambda d: d.update(plan_sha256="g" * 64))

        def failed_command(doc: dict) -> None:
            doc["command_results"][0]["exit_code"] = 1
            doc["unresolved"] = ["pytest failed with exit 1; it has not been fixed"]
        mutation("failed_test_excused_as_implemented", failed_command)

        def unlogged_command(doc: dict) -> None:
            for entry in doc["command_results"]:
                entry.pop("log_path", None)
                entry.pop("log_sha256", None)
        mutation("command_logs_omitted", unlogged_command)
        mutation("false_acceptance_flag", lambda d: d["acceptance_checks"].update(A01=False))

        bad_parent = copy.deepcopy(p00)
        bad_parent["acceptance_checks"]["A01"] = False
        bad_parent["disposition"] = "blocked_implementation"
        parent_path = write("predecessors/P15-00/attempt-0001/TASK_RECEIPT.json", bad_parent)
        cli("failed_parent_control", "task", parent_path)
        child = rebind_child(copy.deepcopy(p01), sha(parent_path))
        cli("child_of_failed_parent", "task", write("child/TASK_RECEIPT.json", child),
            "--receipts-root", out / "predecessors")

        false_phase = {"schema_version": subphase["schema_version"].replace("subphase", "phase"), "phase": "phase-2",
                       "gate": "pass", "phase_1_5_gate": "pass", "task_receipts": {
                           task["id"]: {"path": str(inputs[0]), "sha256": sha(inputs[0]),
                                        "disposition": "implemented_verified"}
                           for task in graph["tasks"] if task["phase"] == "phase-2"}}
        cli("phase_2_closed_using_one_phase_1_5_receipt", "phase", write("false-phase-2.json", false_phase))
        unknown = copy.deepcopy(subphase)
        unknown.update(subphase_id="00-foundaton", task_receipts={}, test_evidence=[])
        cli("unknown_subphase_with_no_tasks", "subphase", write("unknown-subphase.json", unknown))
        false_subphase = copy.deepcopy(subphase)
        false_subphase["task_receipts"]["P15-01"] = {"path": str(inputs[0]), "sha256": sha(inputs[0])}
        cli("subphase_reuses_wrong_task_receipt", "subphase", write("wrong-subphase-task.json", false_subphase))

        evidence = write("lineage/native-row.json", {"row_id": "native-1", "event_at_ns": 5, "available_at_ns": 5})
        lineage = {"schema_version": "research-lineage-manifest-v1", "records": [
            {"record_id": "decision-1", "issue_at_ns": 10, "parents": [
                {"record_id": "native-1", "event_at_ns": 5, "issue_at_ns": 5, "available_at_ns": 5,
                 "artifact_path": str(evidence), "artifact_sha256": sha(evidence), "row_ids": ["native-1"]}]}]}
        cli("valid_lineage", "lineage", write("lineage/valid.json", lineage), expected=0)
        future = copy.deepcopy(lineage)
        future_evidence = write("lineage/future-native-row.json", {
            "row_id": "native-1", "event_at_ns": 100, "available_at_ns": 100})
        future["records"][0]["parents"][0].update(event_at_ns=100, issue_at_ns=100, available_at_ns=100,
                                                 artifact_path=str(future_evidence), artifact_sha256=sha(future_evidence))
        cli("lineage_child_overrides_ancestor_clock", "lineage", write("lineage/future.json", future))
        invalid_clock = copy.deepcopy(lineage)
        invalid_clock["records"][0]["parents"][0]["available_at_ns"] = "tomorrow"
        cli("lineage_invalid_availability_type", "lineage", write("lineage/bad-clock.json", invalid_clock))
        no_hash = copy.deepcopy(lineage)
        no_hash["records"][0]["parents"][0].pop("artifact_sha256")
        cli("lineage_artifact_hash_omitted", "lineage", write("lineage/no-hash.json", no_hash))

        sys.path.insert(0, str(ROOT / "implementation/src"))
        from trading_research.errors import ContractError
        from trading_research.research.contracts.types import Coverage, EvidenceRef, NativeTrade, Reference, Forecast
        early = EvidenceRef("a" * 64, ("earlier-row",), 5, 5, 5, Coverage.COMPLETE, ())
        late = EvidenceRef("a" * 64, ("future-row",), 100, 100, 100, Coverage.COMPLETE, ())
        for label, ref, expected in (("valid", early, "accepted"), ("late", late, "ContractError")):
            event_at = 5 if label == "valid" else 10
            constructor("trade_" + label + "_evidence", lambda ref=ref, event_at=event_at: NativeTrade(
                "t", "NQ:test", event_at, 10, Decimal("100"), 1, 1, ref), expected)
            constructor("reference_" + label + "_evidence", lambda ref=ref: Reference(
                "r", "l", "f", "NQ:test", Decimal("99"), Decimal("101"), 10, 200, (1,), (ref,)), expected)
        constructor("valid_forecast", lambda: Forecast(
            "f", "e", "a" * 64, "s", 10, "h", 20, {"variance": 1.0}, "supported", 4, 5, (), ()), "accepted")
        constructor("forecast_training_ends_after_issue", lambda: Forecast(
            "f", "e", "a" * 64, "s", 10, "h", 20, {"variance": 1.0}, "supported", 100, 5, (), ()), "ContractError")
        if initial_hashes != {str(path): sha(path) for path in inputs}:
            raise RuntimeError("Input bytes changed during the run")
        report = {"schema": "foundation-adversarial-results-v1", "harness_sha256": sha(Path(__file__)),
                  "input_hashes": initial_hashes, "cases": records,
                  "status": "pass" if all(row["passed"] for row in records) else "fail"}
        write("RESULTS.json", report)
        failures = [row["case"] for row in records if not row["passed"]]
        print(json.dumps({"status": report["status"], "cases": len(records), "failures": failures,
                          "results": str(out / "RESULTS.json")}, indent=2))
        return 1 if failures else 0
    except Exception as exc:
        write("HARNESS_ERROR.json", {"error": type(exc).__name__, "detail": str(exc), "cases": records})
        print(f"Harness error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
