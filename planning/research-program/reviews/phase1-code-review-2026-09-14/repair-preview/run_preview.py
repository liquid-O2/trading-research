"""Harness for the B0 vs B0.1 repair-preview. Not a receipt writer.

Monkeypatches event_cache.build_event_window so a cache miss raises instead of
writing under /workspace/data. Invoked from the worktree with PYTHONPATH=src.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal as D
from pathlib import Path
import argparse
import json
import time
import traceback

from trading_research.research.method_pack.historical_features import Q, MINUTE

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


def _stage_details(episode, name):
    for stage in episode.get("stages") or []:
        if stage.get("stage") == name:
            return stage.get("details") or {}
    return {}


def _gb_fail_stop_stats(market, document):
    offset_gt0 = 0
    stop_changed = 0
    for episode in document.get("episodes") or []:
        offset = _stage_details(episode, "five_minute_reclaim").get("confirm_bar_offset")
        if not isinstance(offset, int) or offset <= 0:
            continue
        offset_gt0 += 1
        start = (episode.get("trigger") or {}).get("start")
        if start is None:
            continue
        aligned = start // (5 * MINUTE) * 5 * MINUTE
        try:
            path = market.bars(start, aligned + 5 * MINUTE)
        except Exception:
            continue
        if not path:
            continue
        high = max(row["H"] for row in path)
        low = min(row["L"] for row in path)
        first_stop = high + Q if episode.get("side") == "short" else low - Q
        actual = (episode.get("geometry") or {}).get("stop")
        if actual is None:
            continue
        if D(str(actual)) != D(str(first_stop)):
            stop_changed += 1
    return {"confirm_bar_offset_gt0": offset_gt0, "stop_changed": stop_changed}


def _judas_window_stats(document):
    n = 0
    for episode in document.get("episodes") or []:
        details = _stage_details(episode, "reversal_entry_window")
        failed = episode.get("failed") or []
        if details.get("entry_in_reversal_window") is False or "entry_outside_reversal_window" in failed:
            n += 1
    return {"entry_outside_reversal_window": n}


def _judas_deferred_stats(document):
    pass_n = 0
    fail_window = 0
    fail_other = 0
    unknown_n = 0
    for episode in document.get("episodes") or []:
        failed = episode.get("failed") or []
        verdict = episode.get("research_verdict")
        if verdict == "pass":
            pass_n += 1
        elif verdict == "unknown":
            unknown_n += 1
        elif "reclaim_not_held_at_window" in failed:
            fail_window += 1
        else:
            fail_other += 1
    return {
        "pass": pass_n,
        "fail_reclaim_not_held_at_window": fail_window,
        "fail_other": fail_other,
        "unknown": unknown_n,
        "episodes": pass_n + fail_window + fail_other + unknown_n,
    }


DEFERRED_COVERAGE_ID = "JJ-TBR:branch:judas_reversal_deferred"
JUDAS_COVERAGE_ID = "JJ-TBR:branch:judas_reversal"


def _ensure_judas_deferred_row(rows):
    if any(row["coverage_id"] == DEFERRED_COVERAGE_ID for row in rows):
        return rows
    parent = next((row for row in rows if row["coverage_id"] == JUDAS_COVERAGE_ID), None)
    if parent is None:
        return rows
    return list(rows) + [
        {**parent, "coverage_id": DEFERRED_COVERAGE_ID, "branch": "judas_reversal_deferred"}
    ]


def _b0_row(row):
    """Accepted B0 has no deferred Judas branch; compare that row to native judas_reversal."""
    if row["coverage_id"] != DEFERRED_COVERAGE_ID:
        return row
    return {**row, "coverage_id": JUDAS_COVERAGE_ID, "branch": "judas_reversal"}


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
            b0 = scan_branch(market, _b0_row(row))
            t2 = time.monotonic()
            b01 = scan_branch_repaired(market, row)
            t3 = time.monotonic()
            extras = {}
            if row["method_id"] == "GB-FAIL":
                extras = _gb_fail_stop_stats(market, b01)
            elif row["coverage_id"] == JUDAS_COVERAGE_ID:
                extras = _judas_window_stats(b01)
            elif row["coverage_id"] == DEFERRED_COVERAGE_ID:
                extras = _judas_deferred_stats(b01)
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
                _round4=extras,
                _round5=extras,
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
                    "pass_to_unknown": 0,
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
            slot["pass_to_unknown"] += trans["directions"].get("pass->unknown", 0)
    branches = []
    for cid in sorted(by_branch):
        slot = by_branch[cid]
        slot["directions"] = dict(slot["directions"])
        slot["strategy_status_directions"] = dict(slot["strategy_status_directions"])
        slot["wall_seconds"] = round(slot["wall_seconds"], 4)
        branches.append(slot)
    failed_dates = [item["date"] for item in date_results if not item.get("ok")]
    diagnostics = {
        "gb_fail": {"confirm_bar_offset_gt0": 0, "stop_changed": 0},
        "judas_reversal": {"entry_outside_reversal_window": 0},
        "judas_reversal_deferred": {
            "pass": 0,
            "fail_reclaim_not_held_at_window": 0,
            "fail_other": 0,
            "unknown": 0,
            "episodes": 0,
        },
    }
    for item in date_results:
        for record in item.get("branches") or []:
            extras = record.get("_round5") or record.get("_round4") or {}
            cid = record["coverage_id"]
            if cid.startswith("GB-FAIL:"):
                diagnostics["gb_fail"]["confirm_bar_offset_gt0"] += extras.get("confirm_bar_offset_gt0", 0)
                diagnostics["gb_fail"]["stop_changed"] += extras.get("stop_changed", 0)
            elif cid == JUDAS_COVERAGE_ID:
                diagnostics["judas_reversal"]["entry_outside_reversal_window"] += extras.get(
                    "entry_outside_reversal_window", 0
                )
            elif cid == DEFERRED_COVERAGE_ID:
                for key in diagnostics["judas_reversal_deferred"]:
                    diagnostics["judas_reversal_deferred"][key] += extras.get(key, 0)
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
        "round4_diagnostics": diagnostics,
        "round5_diagnostics": diagnostics,
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
    ]
    if payload.get("round5_note"):
        lines.append(f"- Note: {payload['round5_note']}")
    elif payload.get("round4_note"):
        lines.append(f"- Note: {payload['round4_note']}")
    lines += [
        "",
        "| branch | dates | ep B0 | ep B0.1 | pass B0 | pass B0.1 | fail B0 | fail B0.1 | unknown B0 | unknown B0.1 | no-setup B0 | no-setup B0.1 | verdict changed | directions | pass to unknown (C7) | wall s |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in payload["branches"]:
        directions = ", ".join(f"{k}:{v}" for k, v in sorted(row["directions"].items())) or "—"
        lines.append(
            f"| `{row['coverage_id']}` | {row['dates_run']} | {row['episodes_b0']} | {row['episodes_b01']} | "
            f"{row['pass_b0']} | {row['pass_b01']} | {row['fail_b0']} | {row['fail_b01']} | "
            f"{row['unknown_b0']} | {row['unknown_b01']} | {row['no_setup_b0']} | {row['no_setup_b01']} | "
            f"{row['verdict_changed']} | {directions} | {row.get('pass_to_unknown', 0)} | {row['wall_seconds']:.1f} |"
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


def _row_wanted(row, only):
    if not only:
        return True
    cid = row["coverage_id"]
    method = row["method_id"]
    return cid in only or method in only or any(cid.startswith(f"{token}:") for token in only)


def merge_payload(existing, fresh, refreshed_ids, *, round_key="round5", note=None):
    by_id = {row["coverage_id"]: row for row in existing.get("branches") or []}
    for row in fresh.get("branches") or []:
        by_id[row["coverage_id"]] = row
    existing["branches"] = [by_id[cid] for cid in sorted(by_id)]
    existing[f"{round_key}_note"] = note or "only JJ-TBR rows were refreshed in round five"
    existing[f"{round_key}_refreshed_coverage_ids"] = sorted(refreshed_ids)
    existing[f"{round_key}_wall_seconds_orchestrator"] = fresh.get("wall_seconds_orchestrator")
    existing[f"{round_key}_diagnostics"] = fresh.get("round5_diagnostics") or fresh.get("round4_diagnostics")
    existing[f"{round_key}_date_results"] = fresh.get("date_results")
    existing["n_branches"] = len(existing["branches"])
    return existing


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", default=None, help="method_id prefixes or coverage ids to run")
    parser.add_argument("--merge", action="store_true", help="replace matching rows in existing delta files")
    args = parser.parse_args(argv)
    configure_runtime()
    install_write_guard()
    dates, calendar_n = census_dates()
    registry, manifest = hr.load_registry(PHASE1_RUN, check_software=False)
    wanted = set(affected_branch_ids())
    rows = [slim_row(row) for row in manifest["branches"] if row["coverage_id"] in wanted]
    rows = _ensure_judas_deferred_row(rows)
    present = {row["coverage_id"] for row in rows}
    if present != wanted:
        missing = wanted - present
        raise SystemExit(f"coverage rows missing: {sorted(missing)}")
    if args.only:
        rows = [row for row in rows if _row_wanted(row, args.only)]
        if not rows:
            raise SystemExit(f"no coverage rows matched --only {args.only}")
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
    if args.merge:
        existing = json.loads(json_path.read_text())
        payload = merge_payload(
            existing,
            payload,
            [row["coverage_id"] for row in rows],
            round_key="round5",
            note="only JJ-TBR rows were refreshed in round five",
        )
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    md_path.write_text(render_md(payload))
    print("wrote", json_path)
    print("wrote", md_path)
    print(
        "orchestrator_wall_s",
        payload.get("round5_wall_seconds_orchestrator")
        or payload.get("round4_wall_seconds_orchestrator")
        or payload["wall_seconds_orchestrator"],
    )
    print("round5_diagnostics", json.dumps(payload.get("round5_diagnostics") or {}))


if __name__ == "__main__":
    main()
