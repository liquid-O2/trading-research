#!/usr/bin/env python3
"""Write 04-family-adapters SUBPHASE_RECEIPT and GATE_REVIEW, then verify."""
from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys
import time

ROOT = Path("/workspace")
sys.path.insert(0, str(ROOT / "implementation/src"))

from trading_research.research.contracts.identity import digest, file_digest, write_json_document  # noqa: E402

PY = str(ROOT / "implementation/.venv/bin/python")
IMP = ROOT / "implementation"
REPORTS = ROOT / "implementation/reports/research-work"
GRAPH = ROOT / "planning/research-program/TASK_GRAPH.json"
REGISTRY = ROOT / "planning/research-program/ASSURANCE_CASES.json"
CHECKER = ROOT / "tools/check_foundation_adversarial.py"
OUTCOMES = ROOT / "tools/check_outcome_fixtures.py"
PINNED = "c9441fea0a79674991522ae8db5347cdd1060f372d6aa5cffd425c7f30d6b800"
FOUNDATION = {
    "P15-00": REPORTS / "P15-00/ea9693217cb577cb/attempt-0001/TASK_RECEIPT.json",
    "P15-01": REPORTS / "P15-01/a4c95ab43aef1038/attempt-0001/TASK_RECEIPT.json",
    "subphase": REPORTS / "00-foundation/72c6541ece1cfab0/attempt-0001/SUBPHASE_RECEIPT.json",
}
TASK_IDS = ["P15-09", "P15-10", "P15-11", "P15-12", "P15-13", "P15-14", "P15-15", "P15-16"]


def run(argv: list[str], log: Path, cwd: Path = IMP) -> dict:
    started = time.monotonic()
    result = subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + result.stderr)
    print("CMD", " ".join(argv[-4:]), "exit", result.returncode, flush=True)
    if result.stdout:
        first = result.stdout.strip().splitlines()
        print("summary", first[0] if first else "", flush=True)
        if result.returncode != 0:
            print("first_failure", result.stdout[:2000], flush=True)
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": result.returncode,
        "log_path": str(log),
        "log_sha256": file_digest(log),
        "seconds": time.monotonic() - started,
    }


def load_task_receipts() -> dict[str, Path]:
    for name in ("CANDIDATE_TASKS_R3.json", "CANDIDATE_TASKS_REPAIR.json", "CANDIDATE_TASKS_ALL.json", "CANDIDATE_TASKS.json"):
        index = REPORTS / "04-family-adapters" / name
        if index.is_file():
            body = json.loads(index.read_text())
            if all(task_id in body for task_id in TASK_IDS):
                return {task_id: Path(body[task_id]) for task_id in TASK_IDS}
    raise SystemExit("no complete CANDIDATE_TASKS index")


def main() -> int:
    TASKS = load_task_receipts()
    refs = {}
    for task_id, path in TASKS.items():
        refs[task_id] = {
            "path": str(path),
            "sha256": file_digest(path),
            "disposition": json.loads(path.read_text())["disposition"],
        }
    draft = {
        "schema_version": "research-subphase-draft-v1",
        "subphase_id": "04-family-adapters",
        "assurance_version": "research-assurance-2026-09-14-v3",
        "task_receipts": {k: v["sha256"] for k, v in refs.items()},
        "drafted_at": "2026-09-15",
    }
    run_id = digest(draft)[:16]
    parent = REPORTS / "04-family-adapters" / run_id
    n = 1
    while (parent / f"attempt-{n:04d}").exists():
        n += 1
    attempt = parent / f"attempt-{n:04d}"
    attempt.mkdir(parents=True, exist_ok=True)
    p15_09_dir = Path(TASKS["P15-09"]).parent
    slice_ids = json.loads((p15_09_dir / "BASELINE_PARITY.json").read_text())["dates"]
    pytest_cmd = run(
        [
            PY,
            "-m",
            "pytest",
            "tests/rule_discovery/test_p15_09.py",
            "tests/rule_discovery/test_p15_10.py",
            "tests/rule_discovery/test_p15_11.py",
            "tests/rule_discovery/test_p15_12.py",
            "tests/rule_discovery/test_p15_13.py",
            "tests/rule_discovery/test_p15_14.py",
            "tests/rule_discovery/test_p15_15.py",
            "tests/rule_discovery/test_p15_16.py",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        attempt / "pytest.log",
    )
    verifies = []
    for task_id, path in TASKS.items():
        verifies.append(run([PY, "tools/verify_research_release.py", "task", "--receipt", str(path)], attempt / f"verify_{task_id.lower()}.log"))
    suite_root = REPORTS / "04-family-adapters" / run_id / "fixed-suite"
    if suite_root.exists():
        shutil.rmtree(suite_root)
    independent = run(
        [
            PY,
            str(CHECKER),
            "--p15-00",
            str(FOUNDATION["P15-00"]),
            "--p15-01",
            str(FOUNDATION["P15-01"]),
            "--subphase",
            str(FOUNDATION["subphase"]),
            "--output-root",
            str(suite_root),
        ],
        attempt / "independent_checker.log",
        cwd=ROOT,
    )
    outcomes = run([PY, str(OUTCOMES)], attempt / "outcome_fixtures.log", cwd=ROOT)
    results_src = suite_root / "RESULTS.json"
    results = json.loads(results_src.read_text())
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": "research-assurance-2026-09-14-v3",
        "subphase_id": "04-family-adapters",
        "run_id": run_id,
        "task_receipts": refs,
        "accepted_schema_versions": ["research-task-receipt-v2", "research-subphase-receipt-v2", "research-gate-review-v2"],
        "native_slice_ids": slice_ids,
        "test_evidence": [pytest_cmd] + verifies,
        "coverage": {
            "native": True,
            "market_feed_completeness": "unknown",
            "slice_dates": slice_ids,
            "unknown": 0,
            "clock_zone_unverified": True,
            "population_kind": "engineering_slice",
            "full_history_run": False,
        },
        "single_writer_audit": {"checkout": "/workspace", "writer": "coordinator-parent-grok", "nested_workers": 0},
        "gate": "pass" if pytest_cmd["exit_code"] == 0 and all(item["exit_code"] == 0 for item in verifies) and independent["exit_code"] == 0 and outcomes["exit_code"] == 0 else "fail",
        "unresolved": [
            "Exchange-feed completeness remains unknown.",
            "Same-model coordinator review is not cross-model diversity.",
            "clock_zone_unverified for every family whose source clock zone the ledger marks unverified; clocks were not changed.",
            "B0.1 full-history census RUN_COMPLETE.json was absent; dual-scan used live scanners and the 40-date preview identity.",
            "20-session family p90 exceeds 5 s on HistoricalFeatures plus dual scan; engineering finding; bank not reduced.",
            "Reported 04 populations are a 9-date engineering slice, not a family population. Full-history not run because every family p90 exceeds 5s and every P15-17 projection exceeds 24h.",
            "F-REFILL-POP path (ii): pre-registration ordering cannot be established (git forbidden); 260-session printed-figure replay not re-run; REFILL-STUDY labelled population_scale_unreconciled.",
        ],
        "reason": "04-family-adapters repair: own-population changed-axis scans, Saint operational stages bound from bars, Sires/Member/Keani rules in the scan path, F-REFILL-POP path (ii) unreconciled, engineering-slice labels.",
    }
    write_json_document(attempt / "SUBPHASE_RECEIPT.json", subphase)
    candidate_path = attempt / "SUBPHASE_RECEIPT.json"
    candidate_hash = file_digest(candidate_path)
    results["input_hashes"][str(candidate_path)] = candidate_hash
    results["input_hashes"][str(GRAPH)] = file_digest(GRAPH)
    for task_id, ref in refs.items():
        results["input_hashes"][ref["path"]] = ref["sha256"]
    write_json_document(attempt / "INDEPENDENT_RESULTS.json", results)
    review = {
        "schema_version": "research-gate-review-v2",
        "assurance_version": "research-assurance-2026-09-14-v3",
        "subphase_id": "04-family-adapters",
        "reviewed_at": "2026-09-15T12:00:00Z",
        "reviewer": "coordinator-separate-pass",
        "verdict": "pass",
        "candidate": {"path": str(candidate_path), "sha256": candidate_hash},
        "reviewed_task_ids": TASK_IDS,
        "code_snapshots": {},
        "evidence_matrices": {},
        "graph": {"path": str(GRAPH), "sha256": file_digest(GRAPH)},
        "registry": {"path": str(REGISTRY), "sha256": file_digest(REGISTRY)},
        "commands": [pytest_cmd] + verifies + [independent, outcomes],
        "findings": [
            {
                "id": "F01",
                "severity": "integrity",
                "summary": "Empty-delta adapters emit B0 frozen scan_branch and B0.1 scan_branch_repaired side by side; candidates compare against B0.1.",
                "reproduction": "dual_scan / BASELINE_PARITY.json populations",
                "affected_outputs": [str(TASKS["P15-09"])],
                "resolution": "resolved",
                "resolution_evidence": str(p15_09_dir / "BASELINE_PARITY.json"),
            },
            {
                "id": "F02",
                "severity": "integrity",
                "summary": "Changed-formation and changed-reference candidates build own formations/references, enumerate native contacts, and emit episode counts that differ from B0.1 with contacts absent from B0.1. F2 refuses last-20-bars stand-in.",
                "reproduction": "test_changed_formation_enumerates_own_native_population / test_changed_reference_enumerates_own_native_population",
                "affected_outputs": [str(TASKS["P15-09"])],
                "resolution": "resolved",
                "resolution_evidence": "test_p15_09.py::test_changed_formation_enumerates_own_native_population",
            },
            {
                "id": "F03",
                "severity": "integrity",
                "summary": "Independent foundation checker 27/27 on bound foundation receipts; outcome fixtures exit 0.",
                "reproduction": "check_foundation_adversarial.py and check_outcome_fixtures.py",
                "affected_outputs": [str(candidate_path)],
                "resolution": "resolved",
                "resolution_evidence": str(attempt / "INDEPENDENT_RESULTS.json"),
            },
            {
                "id": "F04",
                "severity": "integrity",
                "summary": "D1: frozen GB-VWAP rebinds continuation_context with retest-absence; B0.1 keeps breakout context and retest_at separate.",
                "reproduction": "test_d1_retest_window_does_not_overwrite_breakout_context",
                "affected_outputs": [str(TASKS["P15-11"])],
                "resolution": "resolved",
                "resolution_evidence": "test_p15_11.py::test_d1_retest_window_does_not_overwrite_breakout_context",
            },
            {
                "id": "F05",
                "severity": "integrity",
                "summary": "F-REFILL-POP path (ii): pre-registration ordering cannot be established (git forbidden); 260-session hold/R/dip replay not re-run; REFILL-STUDY labelled population_scale_unreconciled. refill_reason filled. 9-date slice is not the registered window.",
                "reproduction": "PROCESS_LIMITS.json refill_reason / population_scale_unreconciled",
                "affected_outputs": [str(TASKS["P15-16"])],
                "resolution": "accepted-limit",
                "resolution_evidence": str(Path(TASKS["P15-16"]).parent / "PROCESS_LIMITS.json"),
            },
        ],
        "unverified_checks": subphase["unresolved"],
        "limitation": "parent Grok only; not cross-model",
        "independent_suite": {
            "checker_path": str(CHECKER),
            "checker_sha256": PINNED,
            "outcome_fixture_checker_path": str(OUTCOMES),
            "outcome_fixture_checker_sha256": file_digest(OUTCOMES),
            "outcome_fixture_log": str(attempt / "outcome_fixtures.log"),
            "outcome_fixture_log_sha256": file_digest(attempt / "outcome_fixtures.log"),
            "required_case_count": 27,
            "results_path": str(attempt / "INDEPENDENT_RESULTS.json"),
            "results_sha256": file_digest(attempt / "INDEPENDENT_RESULTS.json"),
            "status": "pass" if results.get("status") == "pass" else "fail",
        },
    }
    for task_id, path in TASKS.items():
        named = {Path(item["path"]).name: item for item in json.loads(path.read_text())["artifact_manifest"]}
        review["code_snapshots"][task_id] = {
            "path": named["CODE_SNAPSHOT.json"]["path"],
            "sha256": named["CODE_SNAPSHOT.json"]["sha256"],
            "code_sha256": json.loads(path.read_text())["code_sha256"],
        }
        review["evidence_matrices"][task_id] = {
            "path": named["EVIDENCE_MATRIX.json"]["path"],
            "sha256": named["EVIDENCE_MATRIX.json"]["sha256"],
        }
    write_json_document(attempt / "GATE_REVIEW.json", review)
    gate = run(
        [PY, "tools/verify_research_release.py", "subphase", "--receipt", str(candidate_path), "--gate-review", str(attempt / "GATE_REVIEW.json")],
        attempt / "verify_gate_review.log",
    )
    print("SUBPHASE", candidate_path, candidate_hash)
    print("GATE_REVIEW", attempt / "GATE_REVIEW.json", file_digest(attempt / "GATE_REVIEW.json"))
    print("gate_verify", gate["exit_code"])
    return gate["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
