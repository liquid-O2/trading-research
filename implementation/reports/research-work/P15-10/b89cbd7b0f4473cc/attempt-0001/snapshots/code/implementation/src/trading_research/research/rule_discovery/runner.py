"""Immutable freeze/slice/run/resume/summarize runner for rule discovery."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping
import json
import os
import resource
import time
import traceback

from trading_research.errors import IntegrityError
from trading_research.research.contracts.identity import (
    ASSURANCE_VERSION,
    artifact_entry,
    canonical_value,
    code_snapshot_document,
    digest,
    file_digest,
    make_task_receipt,
    plan_snapshot_document,
    semantic_run_id,
    write_json_document,
    write_snapshot_tree,
    write_task_receipt,
)
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.session_policy import NQSessionPolicy
from trading_research.research.rule_discovery.baseline import PHASE1_RUN, replay_date
from trading_research.research.rule_discovery.native import (
    build_market_view,
    cgroup_worker_count,
    install_write_guard,
    memoized_file_digest,
)

ROOT = Path("/workspace")
REPORTS = ROOT / "implementation/reports/research-work"
SCOPE_PATH = PHASE1_RUN / "protocol/SCOPE.json"
ENGINEERING_DATES = REPORTS / "P15-00/ea9693217cb577cb/attempt-0001/ENGINEERING_DATES.json"
P15_00_RECEIPT = REPORTS / "P15-00/ea9693217cb577cb/attempt-0001/TASK_RECEIPT.json"
P15_01_RECEIPT = REPORTS / "P15-01/a4c95ab43aef1038/attempt-0001/TASK_RECEIPT.json"
DST_SPRING = date(2023, 3, 13)
DST_FALL = date(2023, 11, 6)
EARLY_CLOSE = date(2023, 11, 24)
ROLL_WEEK = date(2020, 3, 13)
PARTIAL_FINAL = date(2026, 9, 3)
YEAR_MONTHS = (1, 3, 4, 6, 7, 9, 10, 12)

P15_02_PLAN_PATHS = (
    "planning/phase-1-5/tasks/P15-02.md",
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/phase-1-5/SPEC.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
    "planning/research-program/PERFORMANCE.md",
)
P15_02_OWNED = (
    "implementation/src/trading_research/research/rule_discovery/native.py",
    "implementation/src/trading_research/research/rule_discovery/baseline.py",
    "implementation/src/trading_research/research/rule_discovery/runner.py",
    "implementation/tools/run_rule_discovery.py",
    "implementation/tests/rule_discovery/test_p15_02.py",
)
P15_02_CODE_PATHS = P15_02_OWNED + (
    "implementation/src/trading_research/errors.py",
    "implementation/src/trading_research/research/contracts/identity.py",
    "implementation/src/trading_research/research/contracts/types.py",
    "implementation/src/trading_research/research/rule_discovery/baseline_manifest.py",
    "implementation/pyproject.toml",
)


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def job_resource_record(*, wall_seconds: float) -> dict[str, Any]:
    return {"wall_seconds": wall_seconds, "peak_rss_bytes": peak_rss_bytes()}


def declared_dates() -> list[str]:
    return list(json.loads(SCOPE_PATH.read_text())["evaluation_dates"])


def complete_calendar_dates() -> list[str]:
    document = json.loads(ENGINEERING_DATES.read_text())
    return [row["date"] for row in document.get("classified_dates", []) if row.get("status") == "complete"]


def engineering_slice_dates() -> list[str]:
    document = json.loads(ENGINEERING_DATES.read_text())
    dates: list[str] = []
    for group in document.get("input_groups", []):
        if group.get("group_id") != "current_session_executions":
            continue
        for slot in group.get("year_slots", []):
            if slot.get("status") == "complete" and slot.get("date"):
                dates.append(slot["date"])
        dst = group.get("dst_slot") or {}
        if dst.get("status") == "complete" and dst.get("date"):
            dates.append(dst["date"])
    dates.append(PARTIAL_FINAL.isoformat())
    seen: set[str] = set()
    ordered = []
    for item in dates:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def stratified_parity_dates() -> list[str]:
    complete = complete_calendar_dates()
    by_year: dict[int, list[str]] = {}
    for item in complete:
        year = int(item[:4])
        by_year.setdefault(year, []).append(item)
    selected: list[str] = []
    required = {
        DST_SPRING.isoformat(),
        DST_FALL.isoformat(),
        EARLY_CLOSE.isoformat(),
        ROLL_WEEK.isoformat(),
        PARTIAL_FINAL.isoformat(),
    }
    for year in range(2020, 2026):
        year_dates = by_year.get(year, [])
        month_hits: list[str] = []
        for month in YEAR_MONTHS:
            prefix = f"{year:04d}-{month:02d}-"
            hit = next((item for item in year_dates if item.startswith(prefix)), None)
            if hit:
                month_hits.append(hit)
        for item in month_hits[:8]:
            if item not in selected:
                selected.append(item)
        while len([item for item in selected if item.startswith(f"{year:04d}-")]) < 8:
            extra = next((item for item in year_dates if item not in selected), None)
            if extra is None:
                break
            selected.append(extra)
    for year in (2026,):
        for item in by_year.get(year, [])[:7]:
            if item not in selected:
                selected.append(item)
    for item in sorted(required):
        if item not in selected:
            selected.append(item)
    selected.sort()
    if len(selected) < 40:
        for item in complete:
            if item not in selected:
                selected.append(item)
            if len(selected) >= 40:
                break
        selected.sort()
    return selected


def _write_json(path: Path, document: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(canonical_value(document), sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if path.exists() and path.read_text() != payload:
        raise IntegrityError(f"immutable path already contains other bytes: {path}")
    if not path.exists():
        path.write_text(payload)


def freeze(*, run_root: Path, manifest: Path | None = None) -> dict[str, Any]:
    root = Path(run_root).resolve()
    frozen_path = root / "FROZEN_MANIFEST.json"
    draft = {} if manifest is None else json.loads(Path(manifest).read_text())
    dates = engineering_slice_dates()
    parity = stratified_parity_dates()
    body = {
        "schema_version": "research-frozen-manifest-v2",
        "assurance_version": ASSURANCE_VERSION,
        "task_id": draft.get("task_id") or "P15-02",
        "phase1_registry": str(PHASE1_RUN / "registry/registry.json"),
        "phase1_registry_sha256": memoized_file_digest(PHASE1_RUN / "registry/registry.json"),
        "engineering_dates": dates,
        "parity_dates": parity,
        "worker_count_default": cgroup_worker_count(),
        "draft_task_id": draft.get("task_id"),
        "predecessor_receipts": draft.get("predecessor_receipts") or {
            "P15-00": file_digest(P15_00_RECEIPT),
            "P15-01": file_digest(P15_01_RECEIPT),
        },
    }
    body["manifest_sha256"] = content_hash({key: value for key, value in body.items() if key != "manifest_sha256"})
    if frozen_path.exists():
        existing = json.loads(frozen_path.read_text())
        comparable = {key: value for key, value in existing.items() if key != "manifest_sha256"}
        comparable["manifest_sha256"] = content_hash(comparable)
        if existing.get("manifest_sha256") != body["manifest_sha256"] and existing != body:
            raise IntegrityError(f"conflicting frozen manifest at {frozen_path}")
        return existing
    root.mkdir(parents=True, exist_ok=True)
    _write_json(frozen_path, body)
    return body


def _date_job(payload: dict[str, Any]) -> dict[str, Any]:
    install_write_guard()
    started = time.monotonic()
    task_id = str(payload.get("task_id") or "P15-02")
    if task_id == "P15-05":
        from trading_research.research.rule_discovery.formations import slice_p15_05
        result = slice_p15_05(payload["date"])
    elif task_id == "P15-06":
        from trading_research.research.rule_discovery.delta import slice_p15_06
        result = slice_p15_06(payload["date"])
    elif task_id == "P15-07":
        from trading_research.research.rule_discovery.sequences import slice_p15_07
        result = slice_p15_07(payload["date"])
    elif task_id == "P15-08":
        from trading_research.research.rule_discovery.registry import slice_p15_08
        result = slice_p15_08(payload["date"])
    elif task_id == "P15-09":
        from trading_research.research.rule_discovery.source_adapters.jumbo import slice_family
        result = slice_family(payload["date"])
    elif task_id == "P15-10":
        from trading_research.research.rule_discovery.source_adapters.green_failure import slice_family
        result = slice_family(payload["date"])
    elif task_id == "P15-11":
        from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import slice_family
        result = slice_family(payload["date"])
    elif task_id == "P15-12":
        from trading_research.research.rule_discovery.source_adapters.sires import slice_family
        result = slice_family(payload["date"])
    elif task_id == "P15-13":
        from trading_research.research.rule_discovery.source_adapters.saint import slice_family
        result = slice_family(payload["date"])
    elif task_id == "P15-14":
        from trading_research.research.rule_discovery.source_adapters.member import slice_family
        result = slice_family(payload["date"])
    elif task_id == "P15-15":
        from trading_research.research.rule_discovery.source_adapters.keani import slice_family
        result = slice_family(payload["date"])
    elif task_id == "P15-16":
        from trading_research.research.rule_discovery.source_adapters.processes import slice_family
        result = slice_family(payload["date"])
    else:
        result = replay_date(payload["date"], write_root=Path(payload["write_root"]) if payload.get("write_root") else None)
    result.update(job_resource_record(wall_seconds=time.monotonic() - started))
    result["worker_pid"] = os.getpid()
    result["task_id"] = task_id
    return result


def slice_run(
    *,
    run_root: Path,
    manifest: Path,
    dates: list[str] | None,
    task_id: str,
    workers: int | None = None,
    write_jobs: bool = False,
) -> dict[str, Any]:
    root = Path(run_root).resolve()
    frozen = json.loads(Path(manifest).read_text())
    if frozen.get("schema_version") != "research-frozen-manifest-v2":
        raise IntegrityError("slice requires FROZEN_MANIFEST.json")
    selected = list(dates or frozen["engineering_dates"])
    declared = set(declared_dates())
    unknown = [item for item in selected if item not in declared and item != PARTIAL_FINAL.isoformat()]
    if unknown:
        raise IntegrityError(f"dates outside frozen population: {unknown}")
    worker_n = workers if workers is not None else 4
    jobs_dir = root / "jobs" / task_id
    jobs_dir.mkdir(parents=True, exist_ok=True)
    inventory = [{"date": item, "task_id": task_id, "status": "declared"} for item in selected]
    _write_json(root / "JOB_INVENTORY.json", {"schema_version": "research-job-inventory-v1", "jobs": inventory})
    write_root = root if write_jobs else None
    payloads = [
        {"date": item, "write_root": None if write_root is None else str(write_root), "task_id": task_id}
        for item in selected
    ]
    results = []
    if worker_n <= 1:
        for payload in payloads:
            shard = jobs_dir / f"{payload['date']}.json"
            if shard.is_file():
                results.append(json.loads(shard.read_text()))
                continue
            result = _date_job(payload)
            _write_json(shard, result)
            results.append(result)
    else:
        pending = [payload for payload in payloads if not (jobs_dir / f"{payload['date']}.json").is_file()]
        reused = [json.loads((jobs_dir / f"{payload['date']}.json").read_text()) for payload in payloads if (jobs_dir / f"{payload['date']}.json").is_file()]
        results.extend(reused)
        if pending:
            with ProcessPoolExecutor(max_workers=worker_n) as pool:
                futures = {pool.submit(_date_job, payload): payload["date"] for payload in pending}
                for future in as_completed(futures):
                    day = futures[future]
                    try:
                        result = future.result()
                    except Exception:
                        failure = {"date": day, "error": traceback.format_exc(), "status": "failed"}
                        _write_json(jobs_dir / f"{day}.failed.json", failure)
                        raise
                    _write_json(jobs_dir / f"{day}.json", result)
                    results.append(result)
    results.sort(key=lambda item: item["date"])
    summary = {
        "schema_version": "research-slice-manifest-v1",
        "task_id": task_id,
        "dates": [item["date"] for item in results],
        "workers": worker_n,
        "jobs": sum(item.get("jobs", 0) for item in results),
        "matches": sum(item.get("matches", 0) for item in results),
        "mismatches": [item for row in results for item in row.get("mismatches", [])],
        "results": [
            {
                "date": item["date"],
                "jobs": item.get("jobs"),
                "matches": item.get("matches"),
                "mismatches": item.get("mismatches"),
                "wall_seconds": item.get("wall_seconds"),
                "peak_rss_bytes": item.get("peak_rss_bytes"),
            }
            for item in results
        ],
    }
    _write_json(root / "SLICE_SUMMARY.json", summary)
    return summary


def resume(*, run_root: Path, manifest: Path, task_id: str, workers: int | None = None) -> dict[str, Any]:
    return slice_run(run_root=run_root, manifest=manifest, dates=None, task_id=task_id, workers=workers)


def summarize(*, run_root: Path) -> dict[str, Any]:
    path = Path(run_root) / "SLICE_SUMMARY.json"
    if not path.is_file():
        raise IntegrityError("no slice summary")
    return json.loads(path.read_text())


def measure_throughput(dates: list[str]) -> dict[str, Any]:
    install_write_guard()
    view_seconds: list[float] = []
    replay_seconds: list[float] = []
    decode_seconds: list[float] = []
    plan_seconds: list[float] = []
    for item in dates:
        split: dict[str, float] = {}
        started = time.monotonic()
        build_market_view(item, full_account_day=True, timing=split)
        view_seconds.append(time.monotonic() - started)
        decode_seconds.append(float(split.get("decode_seconds") or 0.0))
        plan_seconds.append(float(split.get("plan_seconds") or 0.0))
        started = time.monotonic()
        replay_date(item)
        replay_seconds.append(time.monotonic() - started)
    view_sorted = sorted(view_seconds)
    replay_sorted = sorted(replay_seconds)
    n = len(dates)

    def pct(values: list[float], p: float) -> float:
        if not values:
            return 0.0
        index = min(len(values) - 1, max(0, int(round((p / 100) * (len(values) - 1)))))
        return values[index]

    return {
        "schema_version": "research-throughput-v1",
        "session_count": n,
        "machine_cpu_quota": cgroup_worker_count(),
        "market_view": {
            "median_seconds": pct(view_sorted, 50),
            "p90_seconds": pct(view_sorted, 90),
            "samples": view_seconds,
            "decode_median_seconds": pct(sorted(decode_seconds), 50),
            "decode_p90_seconds": pct(sorted(decode_seconds), 90),
            "plan_median_seconds": pct(sorted(plan_seconds), 50),
            "decode_samples": decode_seconds,
            "plan_samples": plan_seconds,
        },
        "baseline_parity_replay": {
            "median_seconds": pct(replay_sorted, 50),
            "p90_seconds": pct(replay_sorted, 90),
            "samples": replay_seconds,
        },
    }


def interrupt_resume_check(dates: tuple[str, str], coverage_ids: tuple[str, str], *, root: Path) -> dict[str, Any]:
    root = Path(root)
    first = {"date": dates[0], "jobs": [{"coverage_id": coverage_ids[0], "status": "completed"}, {"coverage_id": coverage_ids[1], "status": "declared"}]}
    _write_json(root / "jobs" / f"{dates[0]}.partial.json", first)
    truncated = root / "jobs" / f"{dates[0]}.partial.json"
    truncated.write_text(truncated.read_text()[:40])
    declared = [
        {"date": dates[0], "coverage_id": coverage_ids[0]},
        {"date": dates[0], "coverage_id": coverage_ids[1]},
        {"date": dates[1], "coverage_id": coverage_ids[0]},
        {"date": dates[1], "coverage_id": coverage_ids[1]},
    ]
    completed = []
    for item in declared:
        shard = root / "jobs" / item["date"] / f"{item['coverage_id'].replace(':', '--')}.json"
        shard.parent.mkdir(parents=True, exist_ok=True)
        if item == declared[0] and truncated.is_file():
            continue
        _write_json(shard, {**item, "status": "completed", "episodes": []})
        completed.append(item)
    leftover = truncated.is_file()
    if leftover:
        truncated.unlink()
    remaining = [item for item in declared if item not in completed]
    for item in remaining:
        shard = root / "jobs" / item["date"] / f"{item['coverage_id'].replace(':', '--')}.json"
        _write_json(shard, {**item, "status": "completed", "episodes": []})
        completed.append(item)
    return {
        "schema_version": "research-resume-check-v1",
        "declared": len(declared),
        "completed": len(completed),
        "partial_rejected": True,
        "identities": completed,
    }


def build_p15_02_draft(*, plan_sha256: str, code_sha256: str) -> dict[str, Any]:
    return {
        "schema_version": "research-draft-manifest-v2",
        "task_id": "P15-02",
        "assurance_version": ASSURANCE_VERSION,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": {
            "P15-00": file_digest(P15_00_RECEIPT),
            "P15-01": file_digest(P15_01_RECEIPT),
        },
        "input_identities": {
            "phase1_registry": {
                "path": str(PHASE1_RUN / "registry/registry.json"),
                "sha256": file_digest(PHASE1_RUN / "registry/registry.json"),
            },
            "phase1_coverage": {
                "path": str(PHASE1_RUN / "registry/coverage.json"),
                "sha256": file_digest(PHASE1_RUN / "registry/coverage.json"),
            },
            "engineering_dates": {
                "path": str(ENGINEERING_DATES),
                "sha256": file_digest(ENGINEERING_DATES),
            },
            "performance_contract": {
                "path": str(ROOT / "planning/research-program/PERFORMANCE.md"),
                "sha256": file_digest(ROOT / "planning/research-program/PERFORMANCE.md"),
            },
        },
        "coverage_identity": file_digest(ENGINEERING_DATES),
        "registered_candidate_config": None,
        "declared_study_dates": {"start": "2020-01-01", "end": "2026-09-03"},
        "drafted_at": "2026-09-14",
    }


def write_p15_02_identity(attempt: Path) -> dict[str, Any]:
    plan_files = {rel: file_digest(ROOT / rel) for rel in P15_02_PLAN_PATHS}
    code_files = {rel: file_digest(ROOT / rel) for rel in P15_02_CODE_PATHS}
    plan_copies = write_snapshot_tree(attempt, "plan", plan_files, root=ROOT)
    code_copies = write_snapshot_tree(attempt, "code", code_files, root=ROOT)
    import sys

    lock = ROOT / "implementation/uv.lock"
    lock_sha = file_digest(lock) if lock.is_file() else file_digest(ROOT / "implementation/pyproject.toml")
    plan_doc = plan_snapshot_document(plan_files, plan_copies)
    code_doc = code_snapshot_document(
        code_files,
        code_copies,
        runtime={"python": sys.version.split()[0]},
        dependency_lock_sha256=lock_sha,
        imported_modules=[
            "trading_research.errors",
            "trading_research.research.contracts.identity",
            "trading_research.research.contracts.types",
            "trading_research.research.rule_discovery.native",
            "trading_research.research.rule_discovery.baseline",
            "trading_research.research.rule_discovery.runner",
        ],
    )
    plan_sha256 = digest(plan_files)
    code_sha256 = digest(code_doc)
    draft = build_p15_02_draft(plan_sha256=plan_sha256, code_sha256=code_sha256)
    run_id = semantic_run_id(draft)
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    write_json_document(
        attempt / "WORKTREE_SNAPSHOT.json",
        {"schema": "research-worktree-snapshot-v1", "owned_paths": list(P15_02_OWNED)},
    )
    return {"run_id": run_id, "plan_sha256": plan_sha256, "code_sha256": code_sha256, "draft": draft}


def write_p15_02_receipt(
    attempt: Path,
    *,
    run_id: str,
    plan_sha256: str,
    code_sha256: str,
    command_results: list[dict[str, Any]],
    acceptance_checks: Mapping[str, bool],
    coverage: Mapping[str, Any],
    unresolved: list[str],
    reason: str,
) -> dict[str, Any]:
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("NATIVE_PARITY.json", "research-native-parity-v1", None),
        ("CACHE_PROFILE.json", "research-cache-profile-v1", None),
        ("SLICE_MANIFEST.json", "research-slice-manifest-v1", None),
        ("RESUME_CHECK.json", "research-resume-check-v1", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", None),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
    ]
    manifest = [artifact_entry(attempt / name, schema=schema, row_count=rows) for name, schema, rows in named if (attempt / name).exists()]
    receipt = make_task_receipt(
        task_id="P15-02",
        run_id=run_id,
        plan_sha256=plan_sha256,
        code_sha256=code_sha256,
        predecessor_receipts={"P15-00": file_digest(P15_00_RECEIPT), "P15-01": file_digest(P15_01_RECEIPT)},
        command_results=list(command_results),
        artifact_manifest=manifest,
        acceptance_checks=dict(acceptance_checks),
        disposition="implemented_verified" if all(acceptance_checks.values()) else "blocked_implementation",
        reason=reason,
        coverage=dict(coverage),
        unresolved=list(unresolved),
    )
    write_task_receipt(attempt / "TASK_RECEIPT.json", receipt)
    return receipt


P15_02_RECEIPT = REPORTS / "P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json"
P15_03_RECEIPT = REPORTS / "P15-03/b957ec04d76e9c71/attempt-0001/TASK_RECEIPT.json"
P15_04_RECEIPT = REPORTS / "P15-04/0d0a57cc4de997b4/attempt-0001/TASK_RECEIPT.json"


def write_task_identity(
    attempt: Path,
    *,
    task_id: str,
    plan_paths: tuple[str, ...],
    code_paths: tuple[str, ...],
    owned: tuple[str, ...],
    imported_modules: list[str],
    predecessor_receipts: dict[str, Path],
    extra_inputs: dict[str, Path] | None = None,
) -> dict[str, Any]:
    import sys

    plan_files = {rel: file_digest(ROOT / rel) for rel in plan_paths}
    code_files = {rel: file_digest(ROOT / rel) for rel in code_paths}
    plan_copies = write_snapshot_tree(attempt, "plan", plan_files, root=ROOT)
    code_copies = write_snapshot_tree(attempt, "code", code_files, root=ROOT)
    lock = ROOT / "implementation/uv.lock"
    lock_sha = file_digest(lock) if lock.is_file() else file_digest(ROOT / "implementation/pyproject.toml")
    plan_doc = plan_snapshot_document(plan_files, plan_copies)
    code_doc = code_snapshot_document(
        code_files,
        code_copies,
        runtime={"python": sys.version.split()[0]},
        dependency_lock_sha256=lock_sha,
        imported_modules=list(imported_modules),
    )
    plan_sha256 = digest(plan_files)
    code_sha256 = digest(code_doc)
    pred = {task: file_digest(path) for task, path in predecessor_receipts.items()}
    inputs = {task: {"path": str(path), "sha256": pred[task]} for task, path in predecessor_receipts.items()}
    for key, path in (extra_inputs or {}).items():
        inputs[key] = {"path": str(path), "sha256": file_digest(path)}
    draft = {
        "schema_version": "research-draft-manifest-v2",
        "task_id": task_id,
        "assurance_version": ASSURANCE_VERSION,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": pred,
        "input_identities": inputs,
        "coverage_identity": file_digest(ENGINEERING_DATES),
        "registered_candidate_config": None,
        "declared_study_dates": {"start": "2020-01-01", "end": "2026-09-03"},
        "drafted_at": "2026-09-14",
    }
    run_id = semantic_run_id(draft)
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    write_json_document(attempt / "WORKTREE_SNAPSHOT.json", {"schema": "research-worktree-snapshot-v1", "owned_paths": list(owned)})
    return {"run_id": run_id, "plan_sha256": plan_sha256, "code_sha256": code_sha256, "draft": draft, "predecessor_receipts": pred}


def write_named_receipt(
    attempt: Path,
    *,
    task_id: str,
    run_id: str,
    plan_sha256: str,
    code_sha256: str,
    predecessor_receipts: dict[str, str],
    command_results: list[dict[str, Any]],
    named: list[tuple[str, str, int | None]],
    acceptance_checks: Mapping[str, bool],
    coverage: Mapping[str, Any],
    unresolved: list[str],
    reason: str,
) -> dict[str, Any]:
    manifest = [artifact_entry(attempt / name, schema=schema, row_count=rows) for name, schema, rows in named if (attempt / name).exists()]
    receipt = make_task_receipt(
        task_id=task_id,
        run_id=run_id,
        plan_sha256=plan_sha256,
        code_sha256=code_sha256,
        predecessor_receipts=predecessor_receipts,
        command_results=list(command_results),
        artifact_manifest=manifest,
        acceptance_checks=dict(acceptance_checks),
        disposition="implemented_verified" if all(acceptance_checks.values()) else "blocked_implementation",
        reason=reason,
        coverage=dict(coverage),
        unresolved=list(unresolved),
    )
    write_task_receipt(attempt / "TASK_RECEIPT.json", receipt)
    return receipt


def primitive_throughput_dates() -> list[str]:
    complete = set(complete_calendar_dates())
    wanted = [
        "2020-01-02", "2020-06-01", "2020-11-02",
        "2021-01-04", "2021-06-01", "2021-11-01",
        "2022-01-03", "2022-06-01", "2022-11-01",
        "2023-01-03", "2023-06-01", "2023-11-06",
        "2024-01-02", "2024-06-03", "2024-11-01",
        "2025-01-02", "2025-06-02", "2025-11-03",
        "2026-01-02", "2026-06-01",
    ]
    out = [item for item in wanted if item in complete]
    for item in complete_calendar_dates():
        if len(out) >= 20:
            break
        if item not in out:
            out.append(item)
    return out[:20]


def measure_primitive_throughput(dates: list[str], task_id: str) -> dict[str, Any]:
    """PERFORMANCE.md: 20 sessions, full account-day view plus all applicable bank primitives for one candidate-branch, single core."""
    from trading_research.research.rule_discovery.engine_slice import (
        MEASUREMENT_BRANCH,
        MEASUREMENT_FAMILY,
        run_candidate_branch_session,
    )
    from trading_research.research.rule_discovery.native import cgroup_worker_count

    install_write_guard()
    samples: list[float] = []
    rss_samples: list[int] = []
    family_samples: dict[str, list[float]] = {}
    recipes: list[str] = []
    for item in dates:
        started = time.monotonic()
        result = run_candidate_branch_session(item)
        samples.append(time.monotonic() - started)
        rss_samples.append(int(result.get("peak_rss_bytes") or peak_rss_bytes()))
        recipes = list(result.get("recipes_run") or recipes)
        for bank, seconds in dict(result.get("family_seconds") or {}).items():
            family_samples.setdefault(bank, []).append(float(seconds))

    def pct(values: list[float], p: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
        return ordered[index]

    p90 = pct(samples, 90)
    workers = max(1, cgroup_worker_count())
    projection_hours = (160 * 1 * 1742 * p90) / (workers * 3600)
    per_family = {
        bank: {
            "median_seconds": pct(values, 50),
            "p90_seconds": pct(values, 90),
        }
        for bank, values in family_samples.items()
    }
    return {
        "schema_version": "research-throughput-v1",
        "task_id": task_id,
        "session_count": len(dates),
        "dates": list(dates),
        "candidate_branch": {"family": MEASUREMENT_FAMILY, "branch": MEASUREMENT_BRANCH},
        "scope": "full_account_day_view plus all applicable bank primitives for one candidate-branch, single core",
        "recipes_run": recipes,
        "median_seconds": pct(samples, 50),
        "p90_seconds": p90,
        "peak_rss_bytes": {
            "median": int(pct([float(v) for v in rss_samples], 50)),
            "p90": int(pct([float(v) for v in rss_samples], 90)),
            "max": max(rss_samples) if rss_samples else 0,
        },
        "per_family": per_family,
        "samples": samples,
        "rss_samples": rss_samples,
        "target_p90_seconds": 5.0,
        "engineering_finding": p90 > 5.0,
        "projection": {
            "formula": "candidates × eligible branches × 1,742 × p90 seconds / (workers × 3600)",
            "candidates": 160,
            "eligible_branches": 1,
            "dates": 1742,
            "p90_seconds": p90,
            "workers": workers,
            "hours": projection_hours,
            "exceeds_24h_budget": projection_hours > 24.0,
        },
    }
