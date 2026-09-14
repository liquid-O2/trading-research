"""Harness for the B0 vs B0.1 repair-preview. Not a receipt writer.

Monkeypatches event_cache.build_event_window so a cache miss raises instead of
writing under /workspace/data. Invoked from the worktree with PYTHONPATH=src.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import json
import time
import traceback

from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.measurement_runner import configure_runtime
from trading_research.research.rule_discovery.baseline import PHASE1_RUN
from trading_research.research.rule_discovery.baseline_repairs import (
    BASELINE_REPAIR_VERSION,
    B0_VERSION,
    affected_branch_ids,
)
from trading_research.research.rule_discovery.native import install_write_guard

OUT_DIR = Path(__file__).resolve().parent
MAX_WORKERS = 8


def census_dates():
    root = PHASE1_RUN / "jobs/evaluation"
    dates = sorted(path.name for path in root.iterdir() if path.is_dir() and path.name[:1].isdigit())
    if len(dates) < 40:
        raise SystemExit(f"evaluation calendar too short: {len(dates)}")
    idx = [round(i * (len(dates) - 1) / 39) for i in range(40)]
    return [dates[i] for i in idx], len(dates)


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


def _counts(document):
    episodes = document.get("episodes") or []
    no_setup = 0
    for episode in episodes:
        status = (episode.get("strategy_assessment") or {}).get("status")
        if status == "no_setup":
            no_setup += 1
    return {
        "episodes": len(episodes),
        "pass": sum(episode["research_verdict"] == "pass" for episode in episodes),
        "fail": sum(episode["research_verdict"] == "fail" for episode in episodes),
        "unknown": sum(episode["research_verdict"] == "unknown" for episode in episodes),
        "no_setup": no_setup,
    }


def _transitions(b0, b01):
    left = {episode["candidate_id"]: episode["research_verdict"] for episode in b0.get("episodes") or []}
    right = {episode["candidate_id"]: episode["research_verdict"] for episode in b01.get("episodes") or []}
    shared = set(left) & set(right)
    directions = Counter()
    changed = 0
    for cid in shared:
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


def _process_date(payload):
    day, rows = payload
    install_write_guard()
    configure_runtime()
    from trading_research.research.method_pack import historical_runner as hr
    from trading_research.research.method_pack.historical_features import HistoricalFeatures
    from trading_research.research.method_pack.native_discovery import scan_branch
    from trading_research.research.rule_discovery.baseline import PHASE1_RUN
    from trading_research.research.rule_discovery.baseline_repairs import scan_branch_repaired

    started = time.monotonic()
    try:
        registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
        market = HistoricalFeatures(day, records=hr._records(registry))
    except Exception as exc:
        return {
            "date": day,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "wall_seconds": round(time.monotonic() - started, 4),
            "branches": [],
        }
    results = []
    for row in rows:
        t0 = time.monotonic()
        record = {"coverage_id": row["coverage_id"], "date": day}
        try:
            t1 = time.monotonic()
            b0 = scan_branch(market, row)
            t2 = time.monotonic()
            b01 = scan_branch_repaired(market, row)
            t3 = time.monotonic()
            record.update(
                ok=True,
                b0=_counts(b0),
                b01=_counts(b01),
                transitions=_transitions(b0, b01),
                wall_seconds_b0=round(t2 - t1, 4),
                wall_seconds_b01=round(t3 - t2, 4),
                wall_seconds=round(t3 - t0, 4),
                baseline_version_b0=b0.get("baseline_version"),
                baseline_version_b01=b01.get("baseline_version"),
            )
        except Exception as exc:
            record.update(
                ok=False,
                error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
                wall_seconds=round(time.monotonic() - t0, 4),
            )
        results.append(record)
    return {
        "date": day,
        "ok": True,
        "wall_seconds": round(time.monotonic() - started, 4),
        "branches": results,
    }


def aggregate(date_results, dates, calendar_n):
    by_branch = {}
    for item in date_results:
        for record in item.get("branches") or []:
            cid = record["coverage_id"]
            slot = by_branch.setdefault(
                cid,
                {
                    "coverage_id": cid,
                    "dates_run": 0,
                    "dates_failed": 0,
                    "episodes_b0": 0,
                    "episodes_b01": 0,
                    "pass_b0": 0,
                    "fail_b0": 0,
                    "unknown_b0": 0,
                    "no_setup_b0": 0,
                    "pass_b01": 0,
                    "fail_b01": 0,
                    "unknown_b01": 0,
                    "no_setup_b01": 0,
                    "verdict_changed": 0,
                    "directions": Counter(),
                    "strategy_status_changed": 0,
                    "strategy_status_directions": Counter(),
                    "only_b0": 0,
                    "only_b01": 0,
                    "wall_seconds": 0.0,
                    "errors": [],
                },
            )
            slot["wall_seconds"] += record.get("wall_seconds") or 0
            if not record.get("ok"):
                slot["dates_failed"] += 1
                slot["errors"].append({"date": record.get("date"), "error": record.get("error")})
                continue
            slot["dates_run"] += 1
            for key in ("episodes", "pass", "fail", "unknown", "no_setup"):
                slot[f"{key}_b0"] += record["b0"][key]
                slot[f"{key}_b01"] += record["b01"][key]
            trans = record["transitions"]
            slot["verdict_changed"] += trans["verdict_changed"]
            slot["directions"].update(trans["directions"])
            slot["strategy_status_changed"] += trans["strategy_status_changed"]
            slot["strategy_status_directions"].update(trans["strategy_status_directions"])
            slot["only_b0"] += trans["only_b0"]
            slot["only_b01"] += trans["only_b01"]
    branches = []
    for cid in sorted(by_branch):
        slot = by_branch[cid]
        slot["directions"] = dict(slot["directions"])
        slot["strategy_status_directions"] = dict(slot["strategy_status_directions"])
        slot["wall_seconds"] = round(slot["wall_seconds"], 4)
        branches.append(slot)
    failed_dates = [item["date"] for item in date_results if not item.get("ok")]
    return {
        "schema": "baseline-repair-delta-preview-v1",
        "header": "Preview for the orchestrator, not a receipt. B0 is native_discovery.scan_branch; B0.1 is scan_branch_repaired. No files were written under implementation/reports/phase1-live.",
        "baseline_repair_version": BASELINE_REPAIR_VERSION,
        "b0_version": B0_VERSION,
        "run_root": str(PHASE1_RUN),
        "dates": dates,
        "date_source": f"extract_b.py even spacing: idx=round(i*(N-1)/39) over {calendar_n} run-1.0.1 jobs/evaluation session dates",
        "dates_failed": failed_dates,
        "n_dates": len(dates),
        "n_branches": len(branches),
        "branches": branches,
        "wall_seconds_total": round(sum(item.get("wall_seconds") or 0 for item in date_results), 4),
        "date_results": [
            {
                "date": item["date"],
                "ok": item.get("ok"),
                "wall_seconds": item.get("wall_seconds"),
                "error": item.get("error"),
                "n_branch_ok": sum(1 for rec in item.get("branches") or [] if rec.get("ok")),
                "n_branch_fail": sum(1 for rec in item.get("branches") or [] if not rec.get("ok")),
            }
            for item in date_results
        ],
    }


def render_md(payload):
    lines = [
        "# Baseline repair delta preview",
        "",
        payload["header"],
        "",
        f"- B0: `{payload['b0_version']}` via `native_discovery.scan_branch`",
        f"- B0.1: `{payload['baseline_repair_version']}` via `scan_branch_repaired`",
        f"- Dates: {payload['n_dates']} ({payload['dates'][0]} .. {payload['dates'][-1]})",
        f"- Date source: {payload['date_source']}",
        f"- Branches: {payload['n_branches']}",
        f"- Wall seconds (sum of per-date worker elapsed): {payload['wall_seconds_total']}",
        "",
        "| branch | dates | ep B0 | ep B0.1 | pass B0 | pass B0.1 | fail B0 | fail B0.1 | unknown B0 | unknown B0.1 | no-setup B0 | no-setup B0.1 | verdict changed | directions | wall s |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in payload["branches"]:
        directions = ", ".join(f"{k}:{v}" for k, v in sorted(row["directions"].items())) or "—"
        lines.append(
            f"| `{row['coverage_id']}` | {row['dates_run']} | {row['episodes_b0']} | {row['episodes_b01']} | "
            f"{row['pass_b0']} | {row['pass_b01']} | {row['fail_b0']} | {row['fail_b01']} | "
            f"{row['unknown_b0']} | {row['unknown_b01']} | {row['no_setup_b0']} | {row['no_setup_b01']} | "
            f"{row['verdict_changed']} | {directions} | {row['wall_seconds']:.1f} |"
        )
    if payload["dates_failed"]:
        lines += ["", "## Failed dates", "", ", ".join(payload["dates_failed"])]
    errors = [err for row in payload["branches"] for err in row.get("errors") or []]
    if errors:
        lines += ["", "## Branch errors", ""]
        for err in errors:
            lines.append(f"- `{err['date']}` `{err.get('error')}`")
    lines.append("")
    return "\n".join(lines)


def main():
    configure_runtime()
    install_write_guard()
    dates, calendar_n = census_dates()
    registry, manifest = hr.load_registry(PHASE1_RUN, check_software=False)
    wanted = set(affected_branch_ids())
    rows = [slim_row(row) for row in manifest["branches"] if row["coverage_id"] in wanted]
    if len(rows) != len(wanted):
        missing = wanted - {row["coverage_id"] for row in rows}
        raise SystemExit(f"coverage rows missing: {sorted(missing)}")
    started = time.monotonic()
    date_results = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_process_date, (day, rows)): day for day in dates}
        for future in as_completed(futures):
            day = futures[future]
            result = future.result()
            date_results.append(result)
            print(
                json.dumps(
                    {
                        "date": day,
                        "ok": result.get("ok"),
                        "wall_seconds": result.get("wall_seconds"),
                        "error": result.get("error"),
                    }
                ),
                flush=True,
            )
    date_results.sort(key=lambda item: item["date"])
    payload = aggregate(date_results, dates, calendar_n)
    payload["wall_seconds_orchestrator"] = round(time.monotonic() - started, 4)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "BASELINE_REPAIR_DELTA.json"
    md_path = OUT_DIR / "BASELINE_REPAIR_DELTA.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    md_path.write_text(render_md(payload))
    print("wrote", json_path)
    print("wrote", md_path)
    print("orchestrator_wall_s", payload["wall_seconds_orchestrator"])


if __name__ == "__main__":
    main()
