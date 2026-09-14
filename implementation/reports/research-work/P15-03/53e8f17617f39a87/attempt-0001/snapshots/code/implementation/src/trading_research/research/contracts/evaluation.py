"""Chronological splits, bootstrap, Holm adjustment and baseline diagnostics."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from gzip import GzipFile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import json
import math

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.identity import digest, file_digest
from trading_research.research.method_pack.session_policy import NQSessionPolicy

PHASE1_RUN = Path("/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1")
BOOTSTRAP_SEED = 15022026
BOOTSTRAP_DRAWS = 2000
BLOCK_LENGTH = 5
PRIMARY_SCORE = "mean_daily_net_points_one_mini_benchmark"
FIT_END = date(2021, 12, 31)


def split_manifest(declared_dates: Sequence[str]) -> dict[str, Any]:
    by_year: dict[int, list[str]] = defaultdict(list)
    for item in declared_dates:
        by_year[int(item[:4])].append(item)
    outer = []
    for year in (2022, 2023, 2024, 2025, 2026):
        test = [item for item in by_year.get(year, [])]
        fit_end = date(year - 1, 6, 30)
        tune = [item for item in by_year.get(year - 1, []) if "07-01" <= item[5:] <= "09-30"]
        calibrate = [item for item in by_year.get(year - 1, []) if item[5:] >= "10-01"]
        fit = [item for y in range(2020, year) for item in by_year.get(y, []) if date.fromisoformat(item) <= fit_end]
        outer.append(
            {
                "test_year": year,
                "fit": fit,
                "tune": tune,
                "calibrate": calibrate,
                "test": test,
            }
        )
    return {
        "schema_version": "research-split-manifest-v1",
        "purge": "label interval may not overlap a later partition; one account-day embargo",
        "grouping": "all events from one account day stay together",
        "outer": outer,
        "primary_score": PRIMARY_SCORE,
        "registered_before_search": True,
    }


def account_day_group(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["account_day"])].append(dict(row))
    return dict(grouped)


def overlapping_horizons_same_day(rows: Sequence[Mapping[str, Any]]) -> bool:
    grouped = account_day_group(rows)
    return all(len({row["account_day"] for row in items}) == 1 for items in grouped.values())


def purge_overlap(train: Sequence[str], later: Sequence[str]) -> list[str]:
    later_set = set(later)
    embargo = set()
    for item in later:
        embargo.add(item)
    cleaned = []
    for item in train:
        if item in later_set:
            continue
        nxt = date.fromisoformat(item).toordinal() + 1
        neighbor = date.fromordinal(nxt).isoformat()
        if neighbor in later_set:
            continue
        cleaned.append(item)
    return cleaned


def holm(pvalues: Sequence[float], *, alpha: float = 0.05) -> list[dict[str, Any]]:
    ordered = sorted(enumerate(pvalues), key=lambda item: item[1])
    m = len(ordered)
    rejected = []
    failed = False
    for rank, (index, p) in enumerate(ordered, start=1):
        threshold = alpha / (m - rank + 1)
        accept = (not failed) and p <= threshold
        if not accept:
            failed = True
        rejected.append({"index": index, "p": p, "threshold": threshold, "reject": accept})
    return rejected


def moving_block_bootstrap(values: Sequence[float], *, block: int = BLOCK_LENGTH, draws: int = BOOTSTRAP_DRAWS, seed: int = BOOTSTRAP_SEED) -> np.ndarray:
    array = np.asarray(list(values), dtype=np.float64)
    n = array.size
    if n == 0:
        return np.zeros(draws, dtype=np.float64)
    rng = np.random.Generator(np.random.PCG64(seed))
    block = max(1, int(block))
    starts = rng.integers(0, n, size=(draws, int(math.ceil(n / block))))
    samples = []
    for draw in starts:
        pieces = [array[int(s): int(s) + block] for s in draw]
        concat = np.concatenate(pieces)[:n]
        if concat.size < n:
            concat = np.pad(concat, (0, n - concat.size), mode="wrap")
        samples.append(float(concat.mean()))
    return np.asarray(samples, dtype=np.float64)


def evaluation_protocol() -> dict[str, Any]:
    return {
        "schema_version": "research-evaluation-protocol-v1",
        "primary_score": PRIMARY_SCORE,
        "registered_before_candidate_search": True,
        "bootstrap": {
            "generator": "numpy.random.Generator(PCG64(15022026))",
            "draws": BOOTSTRAP_DRAWS,
            "block_length": BLOCK_LENGTH,
            "sensitivity_blocks": [1, 10],
        },
        "holm_alpha": 0.05,
        "promotion": [
            "software_causality_pass",
            "support_gate",
            "paired_mean_improvement_lb>0",
            "holm_p<=0.05",
            "three_outer_blocks",
            "no_cost_stress_sign_reversal",
        ],
    }


def _job_path(day: str, coverage_id: str) -> Path:
    return PHASE1_RUN / "jobs/evaluation" / day / (coverage_id.replace(":", "--") + ".json.gz")


def _read_job(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with GzipFile(path, "r") as handle:
        return json.loads(handle.read().decode())


def _session_bucket(decision_at: int | None) -> str:
    if decision_at is None:
        return "unknown"
    from trading_research.research.method_pack.clocks import ns_to_et

    local = ns_to_et(int(decision_at))
    minutes = local.hour * 60 + local.minute
    if minutes < 0:
        return "unknown"
    if minutes < 3 * 60:
        return "reopen" if local.hour >= 18 else "asia"
    if minutes < 9 * 60 + 30:
        return "europe" if minutes >= 3 * 60 else "asia"
    if minutes < 12 * 60:
        return "us_morning"
    if minutes < 16 * 60:
        return "us_afternoon"
    return "late"


def baseline_diagnostics(*, end: str = "2021-12-31") -> dict[str, Any]:
    scope = json.loads((PHASE1_RUN / "protocol/SCOPE.json").read_text())
    coverage = json.loads((PHASE1_RUN / "registry/coverage.json").read_text())
    days = [item for item in scope["evaluation_dates"] if item <= end]
    branches = [row for row in coverage["branches"] if not (row["method_id"] == "STOIC-DATA" and row["branch"] == "process_review")]
    families: dict[str, dict[str, Any]] = {}
    for row in branches:
        family = row["method_id"]
        branch = row["coverage_id"]
        key = f"{family}|{branch}"
        cell = families.setdefault(
            key,
            {
                "family": family,
                "branch": branch,
                "terminal": defaultdict(int),
                "ordered": defaultdict(int),
                "mfe": defaultdict(list),
                "mae": defaultdict(list),
                "delay": [],
                "missed_moves": 0,
                "qualified": 0,
                "jobs": 0,
            },
        )
        for day in days:
            path = _job_path(day, branch)
            document = _read_job(path)
            cell["jobs"] += 1
            if document is None:
                cell["terminal"]["unknown_input"] += 1
                continue
            accounting = document.get("session_accounting") or {}
            status = accounting.get("status") or "unknown"
            omissions = accounting.get("active_omissions") or []
            if omissions:
                reason = omissions[0].get("reason") or "prerequisite_rejected"
                cell["terminal"][f"prerequisite:{reason}"] += 1
            elif status:
                cell["terminal"][status] += 1
            for episode in document.get("episodes") or []:
                if episode.get("strategy_assessment", {}).get("status") == "setup":
                    cell["qualified"] += 1
                    decision = episode.get("decision_at")
                    bucket = _session_bucket(decision)
                    contact = None
                    for stage in episode.get("stages") or []:
                        if isinstance(stage, dict) and stage.get("at"):
                            contact = stage["at"]
                            break
                    if contact is not None and decision is not None and decision >= contact:
                        cell["delay"].append((decision - contact) / 1_000_000_000)
                verdict = episode.get("research_verdict") or "unknown"
                cell["ordered"][verdict] += 1
            for outcome in document.get("outcomes") or []:
                cell["ordered"][str(outcome.get("result") or "unknown")] += 1
            for measure in document.get("setup_measurements") or []:
                origin = (measure.get("origin") or {}).get("price")
                bucket = _session_bucket((measure.get("origin") or {}).get("at"))
                for horizon in measure.get("horizons") or []:
                    fav = horizon.get("favorable_points")
                    adv = horizon.get("adverse_points")
                    if fav is not None:
                        cell["mfe"][bucket].append(float(fav))
                    if adv is not None:
                        cell["mae"][bucket].append(float(adv))
                    if fav is not None and float(fav) > 0:
                        cell["missed_moves"] += 1
    summary = []
    for key, cell in sorted(families.items()):
        delays = sorted(cell["delay"])
        def q(values: list[float], p: float) -> float | None:
            if not values:
                return None
            idx = min(len(values) - 1, max(0, int(round(p / 100 * (len(values) - 1)))))
            return values[idx]

        mfe_q = {bucket: {"p50": q(sorted(vals), 50), "p90": q(sorted(vals), 90)} for bucket, vals in cell["mfe"].items()}
        mae_q = {bucket: {"p50": q(sorted(vals), 50), "p90": q(sorted(vals), 90)} for bucket, vals in cell["mae"].items()}
        summary.append(
            {
                "family": cell["family"],
                "branch": cell["branch"],
                "jobs": cell["jobs"],
                "qualified": cell["qualified"],
                "terminal": dict(cell["terminal"]),
                "ordered_outcome_counts": dict(cell["ordered"]),
                "mfe_quantiles": mfe_q,
                "mae_quantiles": mae_q,
                "confirmation_delay_quantiles": {"p50": q(delays, 50), "p90": q(delays, 90)},
                "missed_moves": cell["missed_moves"],
            }
        )
    return {
        "schema_version": "research-baseline-diagnostics-v1",
        "fit_end": end,
        "descriptive_only": True,
        "never_used_to_change_bank_thresholds_or_dates": True,
        "account_days": days,
        "families": summary,
    }


def write_baseline_diagnostics(attempt: Path, *, end: str = "2021-12-31") -> dict[str, Any]:
    document = baseline_diagnostics(end=end)
    payload = json.dumps(document, sort_keys=True, indent=2, default=str) + "\n"
    json_path = attempt / "BASELINE_DIAGNOSTICS.json"
    json_path.write_text(payload)
    lines = [
        "# Baseline diagnostics",
        "",
        "This file is descriptive, fit-period only, and never used to change the bank, thresholds or dates.",
        "",
        f"Fit end: {end}",
        f"Account days: {len(document['account_days'])}",
        f"Family/branch cells: {len(document['families'])}",
        "",
        "| family | branch | jobs | qualified | missed_moves | delay_p50 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in document["families"]:
        lines.append(
            f"| {row['family']} | {row['branch']} | {row['jobs']} | {row['qualified']} | {row['missed_moves']} | {row['confirmation_delay_quantiles']['p50']} |"
        )
    (attempt / "BASELINE_DIAGNOSTICS.md").write_text("\n".join(lines) + "\n")
    return document


P15_03_PLAN_PATHS = (
    "planning/phase-1-5/tasks/P15-03.md",
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/research-program/EVALUATION.md",
    "planning/research-program/OUTCOMES.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
)
P15_03_OWNED = (
    "implementation/src/trading_research/research/contracts/outcomes.py",
    "implementation/src/trading_research/research/contracts/execution.py",
    "implementation/src/trading_research/research/contracts/evaluation.py",
    "implementation/tests/rule_discovery/test_p15_03.py",
)
P15_03_CODE_PATHS = P15_03_OWNED + (
    "implementation/src/trading_research/errors.py",
    "implementation/src/trading_research/research/contracts/identity.py",
    "implementation/src/trading_research/research/contracts/types.py",
    "implementation/pyproject.toml",
)
ROOT = Path("/workspace")
P15_02_RECEIPT_HINT = ROOT / "implementation/reports/research-work/P15-02"


def write_p15_03_identity(attempt: Path, *, predecessor_receipt: Path) -> dict[str, Any]:
    from trading_research.research.contracts.identity import (
        ASSURANCE_VERSION,
        code_snapshot_document,
        digest,
        file_digest,
        plan_snapshot_document,
        semantic_run_id,
        write_json_document,
        write_snapshot_tree,
    )
    import sys

    plan_files = {rel: file_digest(ROOT / rel) for rel in P15_03_PLAN_PATHS}
    code_files = {rel: file_digest(ROOT / rel) for rel in P15_03_CODE_PATHS}
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
        imported_modules=[
            "trading_research.errors",
            "trading_research.research.contracts.identity",
            "trading_research.research.contracts.types",
            "trading_research.research.contracts.outcomes",
            "trading_research.research.contracts.execution",
            "trading_research.research.contracts.evaluation",
        ],
    )
    plan_sha256 = digest(plan_files)
    code_sha256 = digest(code_doc)
    pred_hash = file_digest(predecessor_receipt)
    draft = {
        "schema_version": "research-draft-manifest-v2",
        "task_id": "P15-03",
        "assurance_version": ASSURANCE_VERSION,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": {"P15-02": pred_hash},
        "input_identities": {
            "P15-02": {"path": str(predecessor_receipt), "sha256": pred_hash},
            "phase1_scope": {
                "path": str(PHASE1_RUN / "protocol/SCOPE.json"),
                "sha256": file_digest(PHASE1_RUN / "protocol/SCOPE.json"),
            },
        },
        "coverage_identity": file_digest(PHASE1_RUN / "protocol/SCOPE.json"),
        "registered_candidate_config": None,
        "declared_study_dates": {"start": "2020-01-01", "end": "2026-09-03"},
    }
    run_id = semantic_run_id(draft)
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    write_json_document(attempt / "WORKTREE_SNAPSHOT.json", {"schema": "research-worktree-snapshot-v1", "owned_paths": list(P15_03_OWNED)})
    return {"run_id": run_id, "plan_sha256": plan_sha256, "code_sha256": code_sha256, "draft": draft, "predecessor_hash": pred_hash}


def write_p15_03_receipt(
    attempt: Path,
    *,
    run_id: str,
    plan_sha256: str,
    code_sha256: str,
    predecessor_hash: str,
    command_results: list[dict[str, Any]],
    acceptance_checks: Mapping[str, bool],
    coverage: Mapping[str, Any],
    unresolved: list[str],
    reason: str,
) -> dict[str, Any]:
    from trading_research.research.contracts.identity import artifact_entry, make_task_receipt, write_task_receipt

    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("LABEL_FIXTURES.json", "research-label-fixtures-v1", None),
        ("EXECUTION_FIXTURES.json", "research-execution-fixtures-v1", None),
        ("SPLIT_MANIFEST.json", "research-split-manifest-v1", None),
        ("EVALUATION_PROTOCOL.json", "research-evaluation-protocol-v1", None),
        ("BASELINE_DIAGNOSTICS.json", "research-baseline-diagnostics-v1", None),
        ("BASELINE_DIAGNOSTICS.md", "research-baseline-diagnostics-md-v1", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", None),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
    ]
    manifest = [artifact_entry(attempt / name, schema=schema, row_count=rows) for name, schema, rows in named if (attempt / name).exists()]
    receipt = make_task_receipt(
        task_id="P15-03",
        run_id=run_id,
        plan_sha256=plan_sha256,
        code_sha256=code_sha256,
        predecessor_receipts={"P15-02": predecessor_hash},
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
