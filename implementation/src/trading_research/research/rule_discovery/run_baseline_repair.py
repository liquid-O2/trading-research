"""Full-history B0.1 measurement. Does not edit frozen method_pack or baseline_repairs.

B0 counts are read from run-1.0.1 job files. Cache misses raise instead of writing
under /workspace/data. One session date is the unit of work.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import os
import resource
import sys
import time
import traceback

from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.measurement_runner import (
    configure_runtime,
    measurement_scope,
    session_accounting,
)
from trading_research.research.method_pack.historical_outcomes import observe_outcome
from trading_research.research.method_pack.measurement_outcomes import measure_setup
from trading_research.research.rule_discovery.baseline import PHASE1_RUN
from trading_research.research.rule_discovery.baseline_repairs import (
    BASELINE_REPAIR_VERSION,
    B0_VERSION,
    affected_branch_ids,
    scan_branch_repaired,
)
from trading_research.research.rule_discovery.native import cgroup_worker_count, install_write_guard

ROOT = Path("/workspace")
REPAIRS_PATH = Path(__file__).resolve().parent / "baseline_repairs.py"
RUNNER_PATH = Path(__file__).resolve()
REPORTS_PARENT = ROOT / "implementation/reports/research-work/baseline-repair"
PREVIEW_DELTA = (
    ROOT
    / "planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview"
    / "BASELINE_REPAIR_DELTA.json"
)
MANIFEST_SCHEMA = "baseline-repair-full-history-manifest-v1"
COMPLETION_SCHEMA = "baseline-repair-date-completion-v1"
SUMMARY_SCHEMA = "baseline-repair-full-history-summary-v1"
COMPLETE_SCHEMA = "baseline-repair-run-complete-v1"
REQUESTED_WORKERS = 10
DEFERRED_COVERAGE_ID = "JJ-TBR:branch:judas_reversal_deferred"
COUNT_KEYS = ("episodes", "pass", "fail", "unknown", "no_setup")

_STATE: dict = {}

DECISIONS = [
    "B0 columns are read from run-1.0.1 jobs/evaluation/<date>/<coverage>.json.gz; native scan_branch is not re-run.",
    "judas_reversal_deferred has no B0 job; B0 counts are zeros. B0.1 comes from scan_branch_repaired on the cloned coverage row.",
    "Worker count is 10 by instruction (other runs share the machine), not the cgroup default floor(quota/period).",
    "install_write_guard patches event_cache.build_event_window; a cache miss fails the date instead of writing under /workspace/data.",
    "load_registry(..., check_software=False) because this runner is new code beside frozen baseline_repairs.py.",
    "Job files use the run-1.0.1 measurement job keys plus baseline_version, wall_seconds, peak_rss_bytes.",
    "domain_observations store recipe_id and content sha256 only; the domain/ tree is not written.",
    "Each affected branch is dispatched through scan_branch_repaired, matching the 40-date preview.",
    "peak_rss_bytes is Linux ru_maxrss (kB) * 1024 at job end: worker high-water mark, not an isolated per-job reset.",
    "Resume skips a date with a valid completion.json; otherwise existing job files are kept and missing branches are scanned.",
    "If any date remains failed after one retry, SUMMARY.json, RUN_COMPLETE.json, wiki/current-status.md and PROJECT_HANDOFF.md are not updated; wiki/log.md names the failed dates.",
    "Subphase 03 is not started.",
]


def sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def job_filename(coverage_id: str) -> str:
    return coverage_id.replace(":", "--") + ".json.gz"


def b0_job_path(day: str, coverage_id: str) -> Path:
    return PHASE1_RUN / "jobs/evaluation" / day / job_filename(coverage_id)


def b01_job_path(run_root: Path, day: str, coverage_id: str) -> Path:
    return run_root / "jobs" / day / job_filename(coverage_id)


def slim_row(row):
    return {
        "coverage_id": row["coverage_id"],
        "method_id": row["method_id"],
        "branch": row["branch"],
        "extra_unit": row["extra_unit"],
        "scanner": row["scanner"],
        "source_definition": row["source_definition"],
        "observation_unit": row["observation_unit"],
        "assumption_ids": row["assumption_ids"],
    }


def ensure_judas_deferred_row(rows):
    if any(row["coverage_id"] == DEFERRED_COVERAGE_ID for row in rows):
        return rows
    parent = next((row for row in rows if row["coverage_id"] == "JJ-TBR:branch:judas_reversal"), None)
    if parent is None:
        raise SystemExit("judas_reversal coverage row missing; cannot clone deferred variant")
    return list(rows) + [
        {**parent, "coverage_id": DEFERRED_COVERAGE_ID, "branch": "judas_reversal_deferred"}
    ]


def counts(document):
    episodes = document.get("episodes") or []
    no_setup = 0
    data_unavailable = 0
    for episode in episodes:
        status = (episode.get("strategy_assessment") or {}).get("status")
        if status == "no_setup":
            no_setup += 1
        elif status == "data_unavailable":
            data_unavailable += 1
    return {
        "episodes": len(episodes),
        "pass": sum(episode["research_verdict"] == "pass" for episode in episodes),
        "fail": sum(episode["research_verdict"] == "fail" for episode in episodes),
        "unknown": sum(episode["research_verdict"] == "unknown" for episode in episodes),
        "no_setup": no_setup,
        "data_unavailable": data_unavailable,
    }


def transitions(b0, b01):
    left = {episode["candidate_id"]: episode["research_verdict"] for episode in b0.get("episodes") or []}
    right = {episode["candidate_id"]: episode["research_verdict"] for episode in b01.get("episodes") or []}
    directions = Counter()
    changed = 0
    for cid in set(left) & set(right):
        if left[cid] != right[cid]:
            changed += 1
            directions[f"{left[cid]}->{right[cid]}"] += 1
    sa_left = {
        episode["candidate_id"]: (episode.get("strategy_assessment") or {}).get("status")
        for episode in b0.get("episodes") or []
    }
    sa_right = {
        episode["candidate_id"]: (episode.get("strategy_assessment") or {}).get("status")
        for episode in b01.get("episodes") or []
    }
    sa_directions = Counter()
    sa_changed = 0
    for cid in set(sa_left) & set(sa_right):
        if sa_left[cid] != sa_right[cid]:
            sa_changed += 1
            sa_directions[f"{sa_left[cid]}->{sa_right[cid]}"] += 1
    return {
        "verdict_changed": changed,
        "directions": dict(directions),
        "strategy_status_changed": sa_changed,
        "strategy_status_directions": dict(sa_directions),
        "only_b0": len(set(left) - set(right)),
        "only_b01": len(set(right) - set(left)),
    }


def read_job(path: Path):
    return json.loads(gzip.decompress(path.read_bytes()))


def write_job_atomic(path: Path, document) -> str:
    payload = gzip.compress(
        json.dumps(hr.serializable(document), sort_keys=True, separators=(",", ":"), allow_nan=False).encode(),
        mtime=0,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(payload)
    tmp.replace(path)
    return sha256_bytes(payload)


def write_json_atomic(path: Path, document, *, canonical=False) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if canonical:
        payload = canonical_json(document)
    else:
        payload = (json.dumps(hr.serializable(document), indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(payload)
    tmp.replace(path)
    return sha256_bytes(payload)


def evaluation_dates(registry):
    dates = list(registry["scope"]["evaluation_dates"])
    disk = sorted(
        path.name
        for path in (PHASE1_RUN / "jobs/evaluation").iterdir()
        if path.is_dir() and path.name[:1].isdigit()
    )
    if dates != disk:
        raise SystemExit(f"evaluation calendar mismatch: registry {len(dates)} disk {len(disk)}")
    if len(dates) != 1742:
        raise SystemExit(f"expected 1742 evaluation dates, got {len(dates)}")
    return dates


def preview_dates(dates):
    idx = [round(i * (len(dates) - 1) / 39) for i in range(40)]
    return [dates[i] for i in idx]


def coverage_rows(manifest):
    wanted = set(affected_branch_ids())
    rows = [slim_row(row) for row in manifest["branches"] if row["coverage_id"] in wanted]
    rows = ensure_judas_deferred_row(rows)
    present = {row["coverage_id"] for row in rows}
    if present != wanted:
        raise SystemExit(f"coverage rows missing: {sorted(wanted - present)}")
    order = {cid: i for i, cid in enumerate(affected_branch_ids())}
    rows.sort(key=lambda row: order[row["coverage_id"]])
    return rows


def code_identity():
    return {
        "baseline_repairs_path": "implementation/src/trading_research/research/rule_discovery/baseline_repairs.py",
        "baseline_repairs_sha256": sha256_file(REPAIRS_PATH),
        "python": sys.version.split()[0],
        "runner_path": "implementation/src/trading_research/research/rule_discovery/run_baseline_repair.py",
        "runner_sha256": sha256_file(RUNNER_PATH),
    }


def build_manifest(registry, dates, workers):
    identity = code_identity()
    return {
        "affected_branch_ids": list(affected_branch_ids()),
        "baseline_repair_version": BASELINE_REPAIR_VERSION,
        "baseline_repairs_sha256": identity["baseline_repairs_sha256"],
        "code_identity": identity,
        "dates": list(dates),
        "registry_sha256": registry["registry_sha256"],
        "schema": MANIFEST_SCHEMA,
        "worker_count": workers,
    }


def cpu_quota():
    path = Path("/sys/fs/cgroup/cpu.max")
    if path.is_file():
        text = path.read_text().strip().split()
        if len(text) == 2 and text[0] != "max":
            quota, period = int(text[0]), int(text[1])
            return {"cpu_quota_us": quota, "cpu_period_us": period, "cpu_quota_cpus": quota / period}
    return {"cpu_quota_cpus": None}


def init_run(workers=REQUESTED_WORKERS):
    configure_runtime()
    install_write_guard()
    registry, coverage = hr.load_registry(PHASE1_RUN, check_software=False)
    dates = evaluation_dates(registry)
    rows = coverage_rows(coverage)
    manifest = build_manifest(registry, dates, workers)
    canonical = canonical_json(manifest)
    digest = sha256_bytes(canonical)
    run_id = digest[:16]
    run_root = REPORTS_PARENT / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    manifest_path = run_root / "MANIFEST.json"
    if manifest_path.exists():
        if manifest_path.read_bytes() != canonical:
            raise SystemExit(f"MANIFEST.json at {manifest_path} does not match current canonical bytes")
    else:
        manifest_path.write_bytes(canonical)
        if sha256_file(manifest_path) != digest:
            raise SystemExit("MANIFEST.json hash mismatch after write")
    log_path = run_root / "WORK_LOG.md"
    if not log_path.exists():
        lines = [
            "# B0.1 full-history measurement work log",
            "",
            f"- Run id: `{run_id}`",
            f"- Manifest sha256: `{digest}`",
            f"- Baseline: `{BASELINE_REPAIR_VERSION}`",
            f"- Dates: {len(dates)} ({dates[0]} .. {dates[-1]})",
            f"- Branches: {len(rows)}",
            f"- Jobs: {len(dates) * len(rows)}",
            f"- Workers requested: {workers}",
            f"- cgroup_worker_count: {cgroup_worker_count()}",
            f"- cpu quota: {cpu_quota()}",
            "",
            "## Decisions",
            "",
        ]
        for item in DECISIONS:
            lines.append(f"- {item}")
        lines.append("")
        log_path.write_text("\n".join(lines))
    protocol = registry["scope"]["measurement_protocol"]
    return {
        "run_id": run_id,
        "run_root": run_root,
        "manifest": manifest,
        "manifest_sha256": digest,
        "registry": registry,
        "rows": rows,
        "dates": dates,
        "workers": workers,
        "software_sha256": content_hash(manifest["code_identity"]),
        "measurement_protocol_sha256": protocol["sha256"],
        "registry_sha256": registry["registry_sha256"],
    }


def _observe_outcomes(market, document):
    outcomes = []
    for episode in document.get("episodes") or []:
        try:
            outcomes.append(observe_outcome(market, episode))
        except Exception as exc:
            outcomes.append(
                {
                    "schema": "phase1-post-sequence-observation-v2",
                    "candidate_id": episode.get("candidate_id"),
                    "actual_trade": False,
                    "cost_or_fill_model": False,
                    "sequence_verdict": episode.get("research_verdict"),
                    "result": "not_applicable",
                    "resolved_at": None,
                    "event_ids": [],
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
    return outcomes


def _setup_measurements(market, row, document):
    if measurement_scope(row["method_id"], row["branch"]) != "entry_setup":
        return []
    out = []
    for episode in document.get("episodes") or []:
        if (episode.get("strategy_assessment") or {}).get("status") != "setup":
            continue
        try:
            out.append(measure_setup(market, episode))
        except Exception as exc:
            out.append(
                {
                    "schema": "phase1-setup-price-measurement-v1",
                    "candidate_id": episode.get("candidate_id"),
                    "status": "measurement_error",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
    return out


def _session_accounting(market, document):
    try:
        return session_accounting(market, document)
    except Exception as exc:
        return {"status": "accounting_error", "reason": f"{type(exc).__name__}: {exc}"}


def _domain_receipts(market):
    receipts = {}
    for key, record in getattr(market, "domain_observations", {}).items():
        try:
            digest = content_hash(hr.serializable(record))
        except Exception:
            digest = None
        receipts[key] = {"recipe_id": record.get("recipe_id"), "sha256": digest}
    return receipts


def _finish_document(document, market, row, ctx, wall_seconds, rss):
    ids = [episode["candidate_id"] for episode in document.get("episodes") or []]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate candidate opportunity within branch/session")
    document["outcomes"] = _observe_outcomes(market, document)
    document["setup_measurements"] = _setup_measurements(market, row, document)
    document["session_accounting"] = _session_accounting(market, document)
    receipts = []
    try:
        receipts = list({content_hash(r): r for r in market.input_receipts}.values())
    except Exception:
        receipts = list(market.input_receipts)
    document.update(
        registry_sha256=ctx["registry_sha256"],
        software_sha256=ctx["software_sha256"],
        cohort="evaluation",
        measurement_protocol_sha256=ctx["measurement_protocol_sha256"],
        input_receipts=receipts,
        domain_observations=_domain_receipts(market),
        job_state="completed",
        native_executions=market.window.document["row_count"],
        wall_seconds=wall_seconds,
        peak_rss_bytes=rss,
    )
    if "baseline_version" not in document:
        document["baseline_version"] = BASELINE_REPAIR_VERSION
    return document


def _read_b0(day, coverage_id):
    path = b0_job_path(day, coverage_id)
    if not path.exists():
        return {"episodes": []}
    return read_job(path)


def _init_worker(payload):
    install_write_guard()
    configure_runtime()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    _STATE.clear()
    _STATE.update(payload)
    _STATE["run_root"] = Path(payload["run_root"])


def _completion_ok(path: Path, ctx, rows) -> bool:
    try:
        completion = json.loads(path.read_text())
    except Exception:
        return False
    if completion.get("schema") != COMPLETION_SCHEMA:
        return False
    if completion.get("manifest_sha256") != ctx["manifest_sha256"]:
        return False
    jobs = completion.get("jobs") or []
    if {item["coverage_id"] for item in jobs} != {row["coverage_id"] for row in rows}:
        return False
    for item in jobs:
        job_path = Path(item["path"])
        if not job_path.is_file():
            return False
        if sha256_file(job_path) != item["sha256"]:
            return False
    return True


def _process_date(day):
    install_write_guard()
    configure_runtime()
    started = time.time()
    monotonic0 = time.monotonic()
    ctx = _STATE
    run_root = Path(ctx["run_root"])
    rows = ctx["rows"]
    completion_path = run_root / "jobs" / day / "completion.json"
    if completion_path.exists() and _completion_ok(completion_path, ctx, rows):
        return {
            "date": day,
            "ok": True,
            "resumed": True,
            "wall_seconds": 0.0,
            "started_at": started,
            "finished_at": time.time(),
            "n_jobs": len(rows),
        }
    from trading_research.research.method_pack.historical_features import HistoricalFeatures

    try:
        registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
        market = HistoricalFeatures(day, records=hr._records(registry))
    except Exception as exc:
        payload = {
            "date": day,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "wall_seconds": round(time.monotonic() - monotonic0, 4),
            "started_at": started,
            "finished_at": time.time(),
        }
        write_json_atomic(run_root / "jobs" / day / "FAILURE.json", payload)
        return payload
    jobs = []
    branch_stats = {}
    errors = []
    for row in rows:
        cid = row["coverage_id"]
        path = b01_job_path(run_root, day, cid)
        t0 = time.monotonic()
        try:
            if path.exists():
                document = read_job(path)
                digest = sha256_file(path)
                wall = float(document.get("wall_seconds") or round(time.monotonic() - t0, 4))
                rss = int(document.get("peak_rss_bytes") or peak_rss_bytes())
            else:
                document = scan_branch_repaired(market, row)
                document.pop("deferred_variant", None)
                document = _finish_document(
                    document, market, row, ctx, wall_seconds=0.0, rss=peak_rss_bytes()
                )
                wall = round(time.monotonic() - t0, 4)
                rss = peak_rss_bytes()
                document["wall_seconds"] = wall
                document["peak_rss_bytes"] = rss
                digest = write_job_atomic(path, document)
            b0_doc = _read_b0(day, cid)
            branch_stats[cid] = {
                "b0": counts(b0_doc),
                "b01": counts(document),
                "transitions": transitions(b0_doc, document),
                "wall_seconds": wall,
                "peak_rss_bytes": rss,
                "baseline_version": document.get("baseline_version"),
            }
            jobs.append({"coverage_id": cid, "path": str(path), "sha256": digest})
        except Exception as exc:
            errors.append(
                {
                    "coverage_id": cid,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )
            break
    if errors or len(jobs) != len(rows):
        failure = {
            "date": day,
            "ok": False,
            "error": errors[0]["error"] if errors else f"wrote {len(jobs)}/{len(rows)} jobs",
            "traceback": errors[0]["traceback"] if errors else "",
            "errors": errors,
            "n_jobs_written": len(jobs),
            "wall_seconds": round(time.monotonic() - monotonic0, 4),
            "started_at": started,
            "finished_at": time.time(),
        }
        write_json_atomic(run_root / "jobs" / day / "FAILURE.json", failure)
        return failure
    completion = {
        "schema": COMPLETION_SCHEMA,
        "date": day,
        "manifest_sha256": ctx["manifest_sha256"],
        "registry_sha256": ctx["registry_sha256"],
        "jobs": jobs,
        "branch_stats": branch_stats,
        "native_executions": market.window.document["row_count"],
        "native_input_sha256": market.window.document["input_sha256"],
        "wall_seconds": round(time.monotonic() - monotonic0, 4),
        "peak_rss_bytes": peak_rss_bytes(),
    }
    write_json_atomic(completion_path, completion)
    fail_path = run_root / "jobs" / day / "FAILURE.json"
    if fail_path.exists():
        fail_path.unlink()
    try:
        from trading_research.research.method_pack.strategy_options import option_rows, spot_rows
        from trading_research.research.method_pack.strategy_measurements import vendor_rows

        option_rows.cache_clear()
        spot_rows.cache_clear()
        vendor_rows.cache_clear()
    except Exception:
        pass
    return {
        "date": day,
        "ok": True,
        "resumed": False,
        "wall_seconds": completion["wall_seconds"],
        "started_at": started,
        "finished_at": time.time(),
        "n_jobs": len(jobs),
        "native_executions": completion["native_executions"],
    }


def achieved_concurrency(results):
    events = []
    for item in results:
        start = item.get("started_at")
        end = item.get("finished_at")
        if start is None or end is None:
            continue
        events.append((start, 1))
        events.append((end, -1))
    events.sort()
    current = 0
    peak = 0
    for _t, delta in events:
        current += delta
        if current > peak:
            peak = current
    return peak


def update_progress(run_root: Path, payload):
    write_json_atomic(run_root / "PROGRESS.json", payload)
    (run_root / "HEARTBEAT").write_text(f"{time.time()}\n")


def run_dates(ctx, dates, workers):
    run_root = ctx["run_root"]
    todo = [day for day in dates if not _completion_ok(run_root / "jobs" / day / "completion.json", ctx, ctx["rows"])]
    started = time.monotonic()
    started_wall = time.time()
    results = []
    update_progress(
        run_root,
        {
            "event": "run_started",
            "declared_sessions": len(dates),
            "pending": len(todo),
            "workers": workers,
            "cgroup_worker_count": cgroup_worker_count(),
            "manifest_sha256": ctx["manifest_sha256"],
            "started_at": started_wall,
        },
    )
    print(
        json.dumps(
            {
                "event": "run_started",
                "declared_sessions": len(dates),
                "pending": len(todo),
                "workers": workers,
                "run_id": ctx["run_id"],
            }
        ),
        flush=True,
    )
    if not todo:
        return {
            "date_results": [],
            "wall_seconds_orchestrator": 0.0,
            "failed_dates": [],
            "achieved_concurrency": 0,
        }
    worker_payload = {
        "run_root": str(run_root),
        "rows": ctx["rows"],
        "manifest_sha256": ctx["manifest_sha256"],
        "registry_sha256": ctx["registry_sha256"],
        "software_sha256": ctx["software_sha256"],
        "measurement_protocol_sha256": ctx["measurement_protocol_sha256"],
    }
    failed = []
    completed = 0
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_init_worker,
        initargs=(worker_payload,),
    ) as pool:
        futures = {pool.submit(_process_date, day): day for day in todo}
        for future in as_completed(futures):
            day = futures[future]
            try:
                result = future.result()
            except Exception:
                result = {
                    "date": day,
                    "ok": False,
                    "error": "worker_exception",
                    "traceback": traceback.format_exc(),
                    "started_at": time.time(),
                    "finished_at": time.time(),
                    "wall_seconds": 0.0,
                }
            results.append(result)
            if not result.get("ok"):
                failed.append(day)
            else:
                completed += 1
            print(
                json.dumps(
                    {
                        "event": "date_completed" if result.get("ok") else "date_failed",
                        "date": day,
                        "ok": result.get("ok"),
                        "resumed": result.get("resumed"),
                        "wall_seconds": result.get("wall_seconds"),
                        "error": result.get("error"),
                        "completed": completed,
                        "failed": len(failed),
                        "remaining": len(todo) - completed - len(failed),
                    }
                ),
                flush=True,
            )
            update_progress(
                run_root,
                {
                    "event": "progress",
                    "completed": completed,
                    "failed": len(failed),
                    "remaining": len(todo) - completed - len(failed),
                    "last_date": day,
                    "last_ok": bool(result.get("ok")),
                    "updated_at": time.time(),
                    "failed_dates": list(failed),
                },
            )
    return {
        "date_results": results,
        "wall_seconds_orchestrator": round(time.monotonic() - started, 4),
        "failed_dates": failed,
        "achieved_concurrency": achieved_concurrency(results),
        "worker_count": workers,
    }


def retry_failed(ctx, failed, workers):
    if not failed:
        return {"failed_dates": [], "date_results": [], "wall_seconds_orchestrator": 0.0, "achieved_concurrency": 0}
    print(json.dumps({"event": "retry_started", "dates": failed}), flush=True)
    for day in failed:
        completion = ctx["run_root"] / "jobs" / day / "completion.json"
        if completion.exists():
            completion.unlink()
    return run_dates(ctx, failed, workers)


def load_completion(run_root: Path, day: str):
    return json.loads((run_root / "jobs" / day / "completion.json").read_text())


def _empty_preview_slot():
    return {
        key: 0
        for key in (
            "episodes_b0",
            "episodes_b01",
            "pass_b0",
            "pass_b01",
            "fail_b0",
            "fail_b01",
            "unknown_b0",
            "unknown_b01",
            "no_setup_b0",
            "no_setup_b01",
            "data_unavailable_b0",
            "data_unavailable_b01",
        )
    }


def aggregate(ctx, run_meta):
    run_root = ctx["run_root"]
    dates = ctx["manifest"]["dates"]
    rows = ctx["rows"]
    by_branch = {}
    for row in rows:
        cid = row["coverage_id"]
        by_branch[cid] = {
            "coverage_id": cid,
            "dates_run": 0,
            "dates_failed": 0,
            "episodes_b0": 0,
            "episodes_b01": 0,
            "pass_b0": 0,
            "fail_b0": 0,
            "unknown_b0": 0,
            "no_setup_b0": 0,
            "data_unavailable_b0": 0,
            "pass_b01": 0,
            "fail_b01": 0,
            "unknown_b01": 0,
            "no_setup_b01": 0,
            "data_unavailable_b01": 0,
            "verdict_changed": 0,
            "directions": Counter(),
            "strategy_status_changed": 0,
            "strategy_status_directions": Counter(),
            "only_b0": 0,
            "only_b01": 0,
            "wall_seconds": 0.0,
            "peak_rss_bytes_max": 0,
        }
    missing = []
    for day in dates:
        path = run_root / "jobs" / day / "completion.json"
        if not path.exists():
            missing.append(day)
            continue
        completion = json.loads(path.read_text())
        stats = completion.get("branch_stats") or {}
        for cid, slot in by_branch.items():
            rec = stats.get(cid)
            if rec is None:
                missing.append(f"{day}:{cid}")
                continue
            slot["dates_run"] += 1
            for key in ("episodes", "pass", "fail", "unknown", "no_setup", "data_unavailable"):
                slot[f"{key}_b0"] += rec["b0"][key]
                slot[f"{key}_b01"] += rec["b01"][key]
            trans = rec["transitions"]
            slot["verdict_changed"] += trans["verdict_changed"]
            slot["directions"].update(trans["directions"])
            slot["strategy_status_changed"] += trans["strategy_status_changed"]
            slot["strategy_status_directions"].update(trans["strategy_status_directions"])
            slot["only_b0"] += trans["only_b0"]
            slot["only_b01"] += trans["only_b01"]
            slot["wall_seconds"] += rec.get("wall_seconds") or 0
            rss = rec.get("peak_rss_bytes") or 0
            if rss > slot["peak_rss_bytes_max"]:
                slot["peak_rss_bytes_max"] = rss
    branches = []
    for cid in [row["coverage_id"] for row in rows]:
        slot = by_branch[cid]
        slot["directions"] = dict(slot["directions"])
        slot["strategy_status_directions"] = dict(slot["strategy_status_directions"])
        slot["wall_seconds"] = round(slot["wall_seconds"], 4)
        branches.append(slot)
    sample = preview_dates(dates)
    preview_by_branch = {cid: _empty_preview_slot() for cid in by_branch}
    for day in sample:
        path = run_root / "jobs" / day / "completion.json"
        if not path.exists():
            continue
        stats = json.loads(path.read_text()).get("branch_stats") or {}
        for cid, rec in stats.items():
            if cid not in preview_by_branch:
                continue
            for key in ("episodes", "pass", "fail", "unknown", "no_setup", "data_unavailable"):
                preview_by_branch[cid][f"{key}_b0"] += rec["b0"][key]
                preview_by_branch[cid][f"{key}_b01"] += rec["b01"][key]
    payload = {
        "schema": SUMMARY_SCHEMA,
        "baseline_repair_version": BASELINE_REPAIR_VERSION,
        "b0_version": B0_VERSION,
        "b0_source": "run-1.0.1 jobs/evaluation job files (not rescanned)",
        "run_id": ctx["run_id"],
        "run_root": str(run_root),
        "manifest_sha256": ctx["manifest_sha256"],
        "n_dates": len(dates),
        "n_branches": len(rows),
        "job_count": len(dates) * len(rows),
        "dates_first": dates[0],
        "dates_last": dates[-1],
        "preview_dates": sample,
        "preview_n": len(sample),
        "preview_by_branch": [{"coverage_id": cid, **preview_by_branch[cid]} for cid in sorted(preview_by_branch)],
        "branches": branches,
        "missing": missing,
        "worker_count": ctx["workers"],
        "cgroup_worker_count": cgroup_worker_count(),
        "achieved_concurrency": (run_meta or {}).get("achieved_concurrency"),
        "wall_seconds_orchestrator": (run_meta or {}).get("wall_seconds_orchestrator"),
        "failed_dates": (run_meta or {}).get("failed_dates") or [],
        **cpu_quota(),
    }
    return payload


def render_md(payload):
    lines = [
        "# Baseline repair B0.1 full-history summary",
        "",
        f"- B0: `{payload['b0_version']}` read from run-1.0.1 job files",
        f"- B0.1: `{payload['baseline_repair_version']}` via `scan_branch_repaired`",
        f"- Run id: `{payload['run_id']}`",
        f"- Dates: {payload['n_dates']} ({payload['dates_first']} .. {payload['dates_last']})",
        f"- Branches: {payload['n_branches']}",
        f"- Jobs: {payload['job_count']}",
        f"- Workers requested: {payload['worker_count']}; cgroup default {payload['cgroup_worker_count']}; achieved concurrency {payload.get('achieved_concurrency')}",
        f"- Orchestrator wall seconds: {payload.get('wall_seconds_orchestrator')}",
        "",
        "| branch | dates | ep B0 | ep B0.1 | pass B0 | pass B0.1 | fail B0 | fail B0.1 | unknown B0 | unknown B0.1 | no-setup B0 | no-setup B0.1 | data_unavailable B0 | data_unavailable B0.1 | verdict changed | directions | wall s |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in payload["branches"]:
        directions = ", ".join(f"{k}:{v}" for k, v in sorted(row["directions"].items())) or "—"
        lines.append(
            f"| `{row['coverage_id']}` | {row['dates_run']} | {row['episodes_b0']} | {row['episodes_b01']} | "
            f"{row['pass_b0']} | {row['pass_b01']} | {row['fail_b0']} | {row['fail_b01']} | "
            f"{row['unknown_b0']} | {row['unknown_b01']} | {row['no_setup_b0']} | {row['no_setup_b01']} | "
            f"{row['data_unavailable_b0']} | {row['data_unavailable_b01']} | "
            f"{row['verdict_changed']} | {directions} | {row['wall_seconds']:.1f} |"
        )
    if payload.get("failed_dates"):
        lines += ["", "## Failed dates", "", ", ".join(payload["failed_dates"])]
    lines.append("")
    return "\n".join(lines)


def write_summary(ctx, run_meta):
    payload = aggregate(ctx, run_meta)
    run_root = ctx["run_root"]
    json_path = run_root / "SUMMARY.json"
    md_path = run_root / "SUMMARY.md"
    digest = write_json_atomic(json_path, payload)
    md_path.write_text(render_md(payload))
    if sha256_file(json_path) != digest:
        raise SystemExit("SUMMARY.json hash mismatch")
    return json.loads(json_path.read_text()), digest


def write_run_complete(ctx, payload, summary_sha256, run_meta):
    document = {
        "schema": COMPLETE_SCHEMA,
        "run_id": ctx["run_id"],
        "run_root": str(ctx["run_root"]),
        "manifest_sha256": ctx["manifest_sha256"],
        "summary_sha256": summary_sha256,
        "job_count": payload["job_count"],
        "n_dates": payload["n_dates"],
        "n_branches": payload["n_branches"],
        "failed_dates": payload.get("failed_dates") or [],
        "worker_count": payload["worker_count"],
        "cgroup_worker_count": payload["cgroup_worker_count"],
        "achieved_concurrency": payload.get("achieved_concurrency"),
        "wall_seconds_orchestrator": payload.get("wall_seconds_orchestrator"),
        "completed_at": time.time(),
        **cpu_quota(),
    }
    digest = write_json_atomic(ctx["run_root"] / "RUN_COMPLETE.json", document)
    return document, digest


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=REQUESTED_WORKERS)
    parser.add_argument("--dates", help="comma-separated subset; manifest still lists all 1742")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args(argv)
    workers = args.workers
    ctx = init_run(workers=workers)
    print(
        json.dumps(
            {
                "event": "manifest_ready",
                "run_id": ctx["run_id"],
                "run_root": str(ctx["run_root"]),
                "manifest_sha256": ctx["manifest_sha256"],
                "n_dates": len(ctx["dates"]),
                "n_branches": len(ctx["rows"]),
                "job_count": len(ctx["dates"]) * len(ctx["rows"]),
                "workers": workers,
                "cgroup_worker_count": cgroup_worker_count(),
                **cpu_quota(),
            }
        ),
        flush=True,
    )
    selected = ctx["dates"]
    if args.dates:
        selected = args.dates.split(",")
        unknown = set(selected) - set(ctx["dates"])
        if unknown:
            raise SystemExit(f"dates outside calendar: {sorted(unknown)}")
    run_meta = {
        "failed_dates": [],
        "achieved_concurrency": 0,
        "wall_seconds_orchestrator": 0.0,
        "worker_count": workers,
    }
    if not args.skip_run and not args.summarize_only:
        first = run_dates(ctx, selected, workers)
        failed = list(first.get("failed_dates") or [])
        second = {"date_results": [], "failed_dates": failed, "wall_seconds_orchestrator": 0.0, "achieved_concurrency": 0}
        if failed and not args.dates:
            second = retry_failed(ctx, failed, workers)
            failed = list(second.get("failed_dates") or [])
        run_meta = {
            "failed_dates": failed,
            "achieved_concurrency": max(first.get("achieved_concurrency") or 0, second.get("achieved_concurrency") or 0),
            "wall_seconds_orchestrator": round(
                (first.get("wall_seconds_orchestrator") or 0) + (second.get("wall_seconds_orchestrator") or 0),
                4,
            ),
            "worker_count": workers,
        }
        write_json_atomic(ctx["run_root"] / "RUN_META.json", run_meta)
        if failed:
            print(json.dumps({"event": "run_incomplete", "failed_dates": failed}), flush=True)
            return 2
    remaining = [
        day
        for day in ctx["dates"]
        if not _completion_ok(ctx["run_root"] / "jobs" / day / "completion.json", ctx, ctx["rows"])
    ]
    if remaining:
        print(json.dumps({"event": "not_all_dates", "remaining": len(remaining), "sample": remaining[:12]}), flush=True)
        if args.dates:
            return 0
        return 2
    summary, summary_sha = write_summary(ctx, run_meta)
    complete, complete_sha = write_run_complete(ctx, summary, summary_sha, run_meta)
    print(
        json.dumps(
            {
                "event": "run_complete",
                "run_id": ctx["run_id"],
                "manifest_sha256": ctx["manifest_sha256"],
                "summary_sha256": summary_sha,
                "run_complete_sha256": complete_sha,
                "job_count": complete["job_count"],
                "failed_dates": complete["failed_dates"],
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
