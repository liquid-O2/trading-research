"""Run actual deterministic assertions and preserve code, results and resources."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import io
import json
import math
from pathlib import Path
import platform
import resource
import sys
import time
import unittest

from trading_research.operations.artifacts import ArtifactStore, code_manifest, code_snapshot
from trading_research.operations.scope import Scope

ROOT = Path(__file__).resolve().parents[2]
GROUPS = {
    "contracts": ("tests.test_foundations", "tests.test_calendar", "tests.test_cash_calendar",
                  "tests.test_interval_graph", "tests.test_timer_journal"),
    "registry": ("tests.test_evidence",),
    "labels": ("tests.test_research.LabelTests", "tests.test_research.FoldTests"),
    "provenance": ("tests.test_evidence.ArtifactTests", "tests.test_research.InputLineageTests", "tests.test_research.TrialTests"),
    "market-data": ("tests.test_market_data", "tests.test_compact", "tests.test_decoder_faults", "tests.test_partition_admission", "tests.test_native_fields", "tests.test_arrow_fields"),
    "runtime": ("tests.test_runtime", "tests.test_ports", "tests.test_replay_merge", "tests.test_scheduling", "tests.test_f04_contracts"),
    "risk": ("tests.test_risk",),
    "measurements": ("tests.test_measurements",),
    "data-cohorts": ("tests.test_data_cohorts",),
    "transactions": ("tests.test_transactions", "tests.test_transaction_matching"),
    "quality-joins": ("tests.test_quality_joins",),
    "roll-transitions": ("tests.test_roll_transitions",),
    "shared-bars": ("tests.test_shared_bars",),
    "object-lineage": ("tests.test_object_graph",),
    "artifact-closure": ("tests.test_artifact_graph",),
    "arrival-trace": ("tests.test_arrival",),
    "range-locations": ("tests.test_range_locations",),
    "reference-locations": ("tests.test_reference_locations",),
    "decision-contracts": ("tests.test_decision_contracts",),
    "label-temporal": ("tests.test_v01_v02",),
    "quality": ("tests.test_quality",),
    "objects": ("tests.test_objects",),
    "accounts": ("tests.test_orders_accounting",),
    "execution": ("tests.test_venue", "tests.test_replay", "tests.test_columnar_venue"),
    "definitions": ("tests.test_rolls_definitions", "tests.test_payoffs_registry"),
    "e0": ("tests.test_e0",),
    "batch-review": ("tests.test_batch_review",),
}
OWNERS = {"contracts": ["B00.1", "F02", "F03", "F03.SESSION_CASES", "F04", "F05", "F10"],
          "registry": ["B00.2", "B00.7", "F11", "V08"],
          "labels": ["B00.3", "V01", "V02"], "provenance": ["B00.4", "F11.INPUT_AUDIT", "V03", "V08"],
          "market-data": ["F01.DECODER", "F06.GAP_RECOVERY", "B01.1"],
          "runtime": ["F04", "F04.SCHEDULER", "F12", "B08.5"],
          "risk": ["P07", "P08", "B08.2", "B08.5"],
          "measurements": ["F09", "M01", "M02", "M04", "M05", "M06", "M07", "M09", "B02.1", "B02.2"],
          "data-cohorts": ["F05.CROSS_VENDOR", "B01.4", "B01.5", "B01.8"],
          "transactions": ["F05", "F05.CROSS_VENDOR"],
          "quality-joins": ["F06", "F06.GAP_RECOVERY", "F07", "F07.AGE_SUPPORT"],
          "roll-transitions": ["F08", "F08.ROLL_PARITY"],
          "shared-bars": ["F09", "F09.ACTIVITY_BARS"],
          "object-lineage": ["F10", "F10.LINEAGE"],
          "artifact-closure": ["F11", "F11.INPUT_AUDIT"],
          "arrival-trace": ["F12", "F12.PARITY"],
          "range-locations": ["C01", "C01.RANGE_GEOMETRY", "L01", "L01.INTERNAL_ROLES", "F09"],
          "reference-locations": ["M12", "M12.REFERENCE_TYPES", "L02", "L02.PROJECTION_ROLES", "L03", "L03.RTH_ETH"],
          "decision-contracts": ["B00.6"],
          "label-temporal": ["V01", "V01.LABEL_COVERAGE", "V02", "V02.LINEAGE", "F11"],
          "quality": ["V02", "V03", "V04", "V07", "G03", "B03.2", "B03.4"],
          "objects": ["F10", "M03", "M08", "M13", "B02.3", "B02.4"],
          "accounts": ["P07", "P09", "P11", "B03.1", "B08.2", "B08.3"],
          "execution": ["P01", "P02", "P05", "P06", "P10", "V07", "B00.6", "B03.1"],
          "definitions": ["F02", "F02.PAYOFF", "F08", "B01.1", "B01.5", "B02.3"],
          "e0": ["C01", "L01", "L02", "L17", "V01", "V02", "B03.1", "B03.2"],
          "batch-review": ["F01", "F01.DECODER", "F02", "F04", "F04.SCHEDULER", "F09", "F10",
                           "M06", "M07", "P02", "P07", "P08", "V02", "V03", "V08", "B00.5", "B00.6"]}


def validate_engineering_metrics(module_name, metrics, passed_ids):
    """Bind finite measured evidence to its exact successful assertions.

    The schema is part of the frozen code snapshot, and the recorder applies
    this same boundary again to the immutable result before ledger attachment.
    """
    contracts = json.loads((ROOT / "configs/f09-f12-engineering-metrics.json").read_bytes())
    if (type(module_name) is not str or module_name not in contracts["modules"]
            or type(metrics) is not dict or not metrics
            or type(passed_ids) not in (list, tuple) or any(type(v) is not str for v in passed_ids)):
        raise ValueError("metric module, payload or assertion identities are invalid")
    contract = contracts["modules"][module_name]
    if not set(contract["required_assertions"]) <= set(passed_ids):
        raise ValueError("a required performance/parity assertion did not succeed")
    count = 0

    def finite(value, depth=0):
        nonlocal count
        count += 1
        if depth > 20 or count > 20000:
            raise ValueError("metric evidence exceeds its finite structural bound")
        if type(value) is dict:
            if any(type(k) is not str or not k or len(k) > 256 for k in value):
                raise ValueError("metric keys must be bounded strings")
            for child in value.values():
                finite(child, depth + 1)
        elif type(value) in (list, tuple):
            for child in value:
                finite(child, depth + 1)
        elif type(value) is str:
            if len(value.encode()) > 16384:
                raise ValueError("metric text exceeds its declared bound")
        elif type(value) is float:
            if not math.isfinite(value):
                raise ValueError("nonfinite metric value")
        elif type(value) is int and value.bit_length() > 256:
            raise ValueError("metric integer exceeds its finite representation bound")
        elif value is not None and type(value) not in (int, bool):
            raise ValueError("metric value has an unsupported type")
    finite(metrics)

    def check(value, schema, path):
        if value is None and schema.get("nullable"):
            return
        kind = schema["type"]
        valid = {"object": type(value) is dict, "array": type(value) in (list, tuple),
                 "integer": type(value) is int, "number": type(value) in (int, float),
                 "boolean": type(value) is bool, "string": type(value) is str,
                 "json": True}.get(kind, False)
        if not valid:
            raise ValueError(f"metric {path} requires {kind}")
        if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
            raise ValueError(f"metric {path} differs from its declared constant")
        if kind in {"integer", "number"}:
            if not math.isfinite(value) or value < schema.get("minimum", -math.inf) or value > schema.get("maximum", math.inf):
                raise ValueError(f"metric {path} is outside its declared range")
        if kind in {"array", "string", "object"}:
            if len(value) < schema.get("min_length", 0) or len(value) > schema.get("max_length", 20000):
                raise ValueError(f"metric {path} has an invalid length")
        if kind == "object":
            for key, child in schema.get("required", {}).items():
                if key not in value:
                    raise ValueError(f"required metric {path}.{key} is absent")
                check(value[key], child, path + "." + key)
            if "values" in schema:
                for key, child in value.items():
                    check(child, schema["values"], path + "." + key)
        elif kind == "array" and "items" in schema:
            for index, child in enumerate(value):
                check(child, schema["items"], path + "." + str(index))
    check(metrics, contract["schema"], module_name)


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_ids = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_ids.append(test.id())


def run(group: str, *, evidence_root: Path, plan_root: Path, require_traceability: bool = False,
        progress_stream=None) -> dict:
    store = ArtifactStore(evidence_root / "artifacts")
    snapshot = code_snapshot(ROOT, store)
    expected_code = store.read_json(snapshot)["manifest"]
    started_at = datetime.now(timezone.utc).isoformat()
    start, cpu = time.monotonic(), time.process_time()
    sys.path.insert(0, str(ROOT))
    if group == "all":
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
        groups = list(GROUPS)
    else:
        suite = unittest.defaultTestLoader.loadTestsFromNames(GROUPS[group])
        groups = [group]
    class RetainedProgress(io.StringIO):
        def write(self, value):
            count = super().write(value)
            if progress_stream is not None:
                progress_stream.write(value)
                progress_stream.flush()
            return count

    stream = RetainedProgress()
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
    engineering_metrics, metric_errors = {}, []
    for module_name in ("tests.test_shared_bars", "tests.test_object_graph", "tests.test_artifact_graph", "tests.test_arrival"):
        module = sys.modules.get(module_name)
        if module is None or not any(id.startswith(module_name + ".") for id in result.passed_ids):
            continue
        try:
            metrics = getattr(module, "ENGINEERING_METRICS")
            if type(metrics) is not dict:
                raise TypeError("engineering metrics must be an explicit dictionary")
            validate_engineering_metrics(module_name, metrics, result.passed_ids)
            engineering_metrics[module_name] = json.loads(json.dumps(metrics, allow_nan=False))
        except (AttributeError, TypeError, ValueError) as exc:
            metric_errors.append({"module": module_name, "error": f"{type(exc).__name__}: {exc}"})
    scope = Scope.load(plan_root) if require_traceability or group in {"registry", "all"} else None
    report = {"kind": "executed_engineering_verification", "started_at": started_at,
              "command": [sys.executable, "-m", "trading_research.verify", group],
              "success": result.wasSuccessful() and not result.skipped and not metric_errors and code_manifest(ROOT) == expected_code,
              "code_unchanged_during_run": code_manifest(ROOT) == expected_code,
              "tests_run": result.testsRun, "skipped": [[t.id(), reason] for t, reason in result.skipped],
              "failures": [[t.id(), trace] for t, trace in result.failures],
              "errors": [[t.id(), trace] for t, trace in result.errors],
              "passed_assertion_ids": result.passed_ids,
              "engineering_metrics": engineering_metrics, "engineering_metric_errors": metric_errors,
              "covers": sorted({id for key in groups for id in OWNERS[key]}),
              "coverage_basis": "Named assertions only; broader unit, phase and source-clause completion is not inferred.",
              "scope_version": scope.version if scope else None, "code_snapshot": asdict(snapshot),
              "python": platform.python_version(), "platform": platform.platform(),
              "wall_seconds": time.monotonic() - start, "cpu_seconds": time.process_time() - cpu,
              "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
              "test_log": stream.getvalue(), "economic_runs": 0}
    ref = store.put_json(report, kind="verification")
    return {"success": report["success"], "tests_run": result.testsRun, "passed": len(result.passed_ids),
            "skipped": len(result.skipped), "failures": len(result.failures), "errors": len(result.errors),
            "report": str(store.path(ref)), "artifact": asdict(ref), "code_snapshot": asdict(snapshot)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=(*GROUPS, "all"))
    parser.add_argument("--suite", choices=("all",), default="all")
    parser.add_argument("--fixtures", choices=("hand_checked", "mutation_and_restart"))
    parser.add_argument("--require-traceability", action="store_true")
    parser.add_argument("--evidence-root", type=Path, default=ROOT / "evidence")
    parser.add_argument("--plan-root", type=Path, default=ROOT.parent / "planning/trading-model")
    args = parser.parse_args(argv)
    result = run(args.group, evidence_root=args.evidence_root, plan_root=args.plan_root,
                 require_traceability=args.require_traceability)
    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
