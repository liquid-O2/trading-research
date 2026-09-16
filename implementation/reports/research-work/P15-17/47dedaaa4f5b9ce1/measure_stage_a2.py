"""P15-17 stage A round 3 measurement.

Per date, on one account-day view:
  1. raw load;
  2. warm_session data plane (failures recorded by name, never swallowed);
  3. FRESH column: each of the seven RA-5 candidates scanned as the first touch
     of its (family, branch) on this session -- the true cold per-candidate cost;
  4. WARM REPEAT column: the same seven scanned again;
  5. branch prepay: warm_session over every remaining distinct (family, branch),
     which also returns the B0.2 baselines used for the verdict diff;
  6. whole bank: all supported candidates, timed.

per-session seconds = load + data plane + fresh + prepay + bank. The warm-repeat
column is a measurement artifact and is excluded from it.

Writes THROUGHPUT_B02.json (projection from the FRESH column) and
VERDICT_CHANGES.json (the full candidate x date table, per-bank counts derived
from it in the same file).

Run from implementation/ with PYTHONPATH=src.
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

from trading_research.research.rule_discovery import search

ROOT = Path("reports/research-work/P15-17/47dedaaa4f5b9ce1")
PHASE1_MEAN_SECONDS = 2.8859749833826815


def main() -> int:
    dates = search.r3_dates()
    resolved = search.resolve_bank()
    supported = [item for item in resolved if item.supported]
    by_id = {item.candidate_id: item for item in resolved}
    seven = [by_id[cid] for cid in search.THROUGHPUT_CANDIDATE_IDS]
    assert len({(item.family, item.branch) for item in seven}) == len(seven), "seven RA-5 branches must be distinct"
    all_branches = sorted({(item.family, item.branch) for item in supported})

    fresh: dict[str, list[float]] = {item.candidate_id: [] for item in seven}
    warm_repeat: dict[str, list[float]] = {item.candidate_id: [] for item in seven}
    scan_times: dict[str, list[float]] = {item.candidate_id: [] for item in supported}
    load_times: list[float] = []
    data_plane_times: list[float] = []
    prepay_times: list[float] = []
    bank_times: list[float] = []
    session_times: list[float] = []
    warm_failures: list[dict] = []
    table: list[dict] = []

    for day in dates:
        t0 = time.perf_counter()
        market = search.load_b02_market(day, warm=False)
        raw_load = time.perf_counter() - t0
        load_times.append(raw_load)

        plane = search.warm_session(market)
        data_plane_times.append(plane["data_plane_seconds"])
        for failure in plane["failures"]:
            warm_failures.append({"date": day, "phase": "data_plane", **failure})

        fresh_total = 0.0
        for item in seven:
            started = time.perf_counter()
            search.scan_candidate(market, item)
            elapsed = time.perf_counter() - started
            fresh[item.candidate_id].append(elapsed)
            fresh_total += elapsed
        for item in seven:
            started = time.perf_counter()
            search.scan_candidate(market, item)
            warm_repeat[item.candidate_id].append(time.perf_counter() - started)

        prepay = search.warm_session(market, branches=all_branches)
        prepay_times.append(prepay["branch_prepay_seconds"])
        for failure in prepay["failures"]:
            warm_failures.append({"date": day, "phase": "branch_prepay", **failure})
        baselines = prepay["baselines"]

        bank_started = time.perf_counter()
        for item in supported:
            started = time.perf_counter()
            document = search.scan_candidate(market, item)
            scan_times[item.candidate_id].append(time.perf_counter() - started)
            diff = search.verdict_changed(baselines[(item.family, item.branch)], document)
            table.append(
                {
                    "candidate_id": item.candidate_id,
                    "date": day,
                    "bank": item.bank,
                    "family": item.family,
                    "branch": item.branch,
                    "episode_verdict_changed": diff["episode_verdict_changed"],
                    "stage_verdict_changed": diff["stage_verdict_changed"],
                    "contact_population_changed": diff["contacts_changed"],
                    "baseline_contacts": diff["baseline_contacts"],
                    "candidate_contacts": diff["candidate_contacts"],
                }
            )
        bank_seconds = time.perf_counter() - bank_started
        bank_times.append(bank_seconds)
        session_times.append(raw_load + plane["data_plane_seconds"] + fresh_total + prepay["branch_prepay_seconds"] + bank_seconds)
        print(
            f"{day} load {raw_load:6.2f} plane {plane['data_plane_seconds']:6.2f} fresh {fresh_total:7.2f} "
            f"prepay {prepay['branch_prepay_seconds']:7.2f} bank {bank_seconds:7.2f}",
            flush=True,
        )

    pct = search._percentile
    rows = []
    for item in seven:
        f = fresh[item.candidate_id]
        w = warm_repeat[item.candidate_id]
        rows.append(
            {
                "candidate_id": item.candidate_id,
                "family": item.family,
                "branch": item.branch,
                "bank": item.bank,
                "recipe_id": item.recipe_id,
                "phase": item.phase,
                "hooks": list(item.hooks),
                "n_dates": len(f),
                "fresh_median_seconds": statistics.median(f),
                "fresh_p90_seconds": pct(f, 0.90),
                "warm_repeat_median_seconds": statistics.median(w),
                "warm_repeat_p90_seconds": pct(w, 0.90),
                "median_seconds": statistics.median(f),
                "p90_seconds": pct(f, 0.90),
                "fresh_per_date_seconds": f,
                "warm_repeat_per_date_seconds": w,
            }
        )
    fresh_p90 = max(row["fresh_p90_seconds"] for row in rows)
    warm_p90 = max(row["warm_repeat_p90_seconds"] for row in rows)
    session_p90 = pct(session_times, 0.90)
    all_warm = [v for s in scan_times.values() for v in s]

    def project_contract(workers: int, p90: float, label: str) -> dict:
        hours = 160 * 1742 * p90 / (workers * 3600)
        return {
            "workers": workers,
            "hours": hours,
            "exceeds_24h_budget": hours > 24.0,
            "formula": f"160 x 1,742 x {label} p90 / (workers x 3600)",
            "p90_seconds": p90,
            "candidates": 160,
            "dates": 1742,
        }

    def project_session(workers: int) -> dict:
        hours = 1742 * session_p90 / (workers * 3600)
        return {
            "workers": workers,
            "hours": hours,
            "exceeds_24h_budget": hours > 24.0,
            "formula": "1,742 x per-session p90 / (workers x 3600)",
            "per_session_p90_seconds": session_p90,
            "dates": 1742,
        }

    payload = {
        "schema_version": "research-p15-17-throughput-b02-v3",
        "measured_at": "2026-09-16",
        "engine": (
            "per-session data plane plus per-(family, branch) cold-scan prepay; whole bank evaluated "
            "on one loaded account-day view"
        ),
        "columns": {
            "fresh": "first scan of that (family, branch) on the session, after the data-plane warm only",
            "warm_repeat": "second scan of the same candidate on the same session",
        },
        "dates": list(dates),
        "candidates": rows,
        "supported_candidates": len(supported),
        "distinct_branches": len(all_branches),
        "warm_failures": warm_failures,
        "load_median_seconds": statistics.median(load_times),
        "load_p90_seconds": pct(load_times, 0.90),
        "data_plane_median_seconds": statistics.median(data_plane_times),
        "branch_prepay_median_seconds": statistics.median(prepay_times),
        "branch_prepay_p90_seconds": pct(prepay_times, 0.90),
        "whole_bank_median_seconds": statistics.median(bank_times),
        "whole_bank_p90_seconds": pct(bank_times, 0.90),
        "per_session_median_seconds": statistics.median(session_times),
        "per_session_p90_seconds": session_p90,
        "per_session_seconds": session_times,
        "pipeline_median_seconds": statistics.median([row["fresh_median_seconds"] for row in rows]),
        "pipeline_p90_seconds": fresh_p90,
        "warm_repeat_p90_seconds": warm_p90,
        "projection": {
            "workers_17": project_contract(17, fresh_p90, "fresh"),
            "workers_12": project_contract(12, fresh_p90, "fresh"),
        },
        "projection_warm_repeat": {
            "workers_17": project_contract(17, warm_p90, "warm-repeat"),
            "workers_12": project_contract(12, warm_p90, "warm-repeat"),
        },
        "projection_per_session": {"workers_17": project_session(17), "workers_12": project_session(12)},
        "r3_gate": {
            "fresh_p90_seconds": fresh_p90,
            "warm_repeat_p90_seconds": warm_p90,
            "phase1_mean_seconds": PHASE1_MEAN_SECONDS,
            "mean_multiple_warm": PHASE1_MEAN_SECONDS / statistics.mean(all_warm),
            "target_p90_seconds": 5.0,
            "meets_target_p90_fresh": fresh_p90 <= 5.0,
            "meets_target_p90_warm": warm_p90 <= 5.0,
        },
        "cgroup_workers_floor": 17,
    }
    (ROOT / "THROUGHPUT_B02.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    per_bank: dict[str, dict] = {}
    for bank in search.BANKS:
        rows_b = [r for r in table if r["bank"] == bank]
        changed = [
            r for r in rows_b
            if r["episode_verdict_changed"] or r["stage_verdict_changed"] or r["contact_population_changed"]
        ]
        per_bank[bank] = {
            "candidate_dates_evaluated": len(rows_b),
            "candidate_dates_changed": len(changed),
            "candidate_dates_with_episode_verdict_change": sum(1 for r in rows_b if r["episode_verdict_changed"]),
            "candidate_dates_with_stage_verdict_change": sum(1 for r in rows_b if r["stage_verdict_changed"]),
            "candidate_dates_with_contact_population_change": sum(1 for r in rows_b if r["contact_population_changed"]),
            "distinct_candidates_changed": sorted({r["candidate_id"] for r in changed}),
        }
    (ROOT / "VERDICT_CHANGES.json").write_text(
        json.dumps(
            {
                "schema_version": "research-p15-17-verdict-changes-v2",
                "dates": list(dates),
                "supported_candidates": len(supported),
                "rows_are_the_source_of_truth": (
                    "per_bank is derived from rows; recompute it by grouping rows on bank and counting "
                    "each flag. changed = episode_verdict_changed or stage_verdict_changed or "
                    "contact_population_changed."
                ),
                "n_rows": len(table),
                "per_bank": per_bank,
                "rows": table,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(f"wrote THROUGHPUT_B02.json and VERDICT_CHANGES.json ({len(table)} rows)")
    print(f"fresh p90 {fresh_p90:.3f}s warm-repeat p90 {warm_p90:.3f}s per-session p90 {session_p90:.2f}s")
    print(f"warm failures: {len(warm_failures)}")
    for bank, row in per_bank.items():
        print(f"  {bank:10s} {row['candidate_dates_changed']:5d}/{row['candidate_dates_evaluated']:5d} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
