"""Track R3 throughput, family re-measure, cProfile, and census hash check."""

from __future__ import annotations

from pathlib import Path
import cProfile
import io
import json
import pstats
import time

from trading_research.research.rule_discovery.census_reader import open_census
from trading_research.research.rule_discovery.engine_slice import run_candidate_branch_session
from trading_research.research.rule_discovery.kernels import warmup_kernels
from trading_research.research.rule_discovery.native import cgroup_worker_count, install_write_guard
from trading_research.research.rule_discovery.runner import (
    job_resource_record,
    measure_primitive_throughput,
    peak_rss_bytes,
    primitive_throughput_dates,
)
from trading_research.research.rule_discovery.source_adapters.common import PRIMARY_BRANCH

ROOT = Path("/workspace/.worktrees/stage-a-r3/implementation/reports/research-work/P15-17/_track_r3")
REPORTS = Path("/workspace/implementation/reports/research-work")
PHASE1_MEAN_SECONDS = 79.6 * 3600 / (57 * 1742)
TARGET_MEAN_SECONDS = PHASE1_MEAN_SECONDS / 3.0
TARGET_P90_SECONDS = 5.0
BEFORE_THROUGHPUT = {
    "P15-09": REPORTS / "P15-09/72323a6d8f65b77d/attempt-0001/THROUGHPUT.json",
    "P15-10": REPORTS / "P15-10/a856814fe11b24ac/attempt-0001/THROUGHPUT.json",
    "P15-11": REPORTS / "P15-11/a3f84244bc9239c3/attempt-0001/THROUGHPUT.json",
    "P15-12": REPORTS / "P15-12/2488a221f5843c26/attempt-0001/THROUGHPUT.json",
    "P15-13": REPORTS / "P15-13/79e50a6a3faf8be2/attempt-0001/THROUGHPUT.json",
    "P15-14": REPORTS / "P15-14/31841425087b5507/attempt-0001/THROUGHPUT.json",
    "P15-15": REPORTS / "P15-15/f7df59d81e058166/attempt-0001/THROUGHPUT.json",
    "P15-16": REPORTS / "P15-16/316dc53caf8bdfac/attempt-0001/THROUGHPUT.json",
}


def _write(path: Path, document) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, sort_keys=True, indent=2, default=str) + "\n")


def _pct(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
    return ordered[index]


def _profile(path: Path, day: str) -> float:
    profiler = cProfile.Profile()
    started = time.monotonic()
    profiler.enable()
    run_candidate_branch_session(day)
    profiler.disable()
    elapsed = time.monotonic() - started
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).sort_stats("cumtime").print_stats(20)
    path.write_text(f"session={day} wall_seconds={elapsed:.6f}\n{stream.getvalue()}")
    return elapsed


def _family_plane(dates: list[str], family: str, branch: str) -> dict:
    """Account-day view plus applicable bank primitives. Not the family adapter scan."""
    samples: list[float] = []
    rss: list[int] = []
    for item in dates:
        started = time.monotonic()
        run_candidate_branch_session(item, family=family, branch=branch)
        samples.append(time.monotonic() - started)
        rss.append(peak_rss_bytes())
    return {
        "family": family,
        "branch": branch,
        "scope": "full_account_day_view plus all applicable bank primitives for one candidate-branch, single core",
        "plane_median_seconds": _pct(samples, 50),
        "plane_p90_seconds": _pct(samples, 90),
        "samples": samples,
        "peak_rss_bytes": {
            "median": int(_pct([float(v) for v in rss], 50)),
            "p90": int(_pct([float(v) for v in rss], 90)),
            "max": max(rss) if rss else 0,
        },
    }


def main() -> None:
    install_write_guard()
    ROOT.mkdir(parents=True, exist_ok=True)
    warmup_kernels()
    dates = primitive_throughput_dates()
    census = open_census()
    hash_check = census.hash_check()
    _write(ROOT / "CENSUS_HASH_CHECK.json", hash_check)
    print("census_hash_check", json.dumps(hash_check, sort_keys=True))

    after_elapsed = _profile(ROOT / "PROFILE_AFTER.txt", "2024-03-05")
    print("profile_after_2024-03-05", round(after_elapsed, 3))

    candidate = measure_primitive_throughput(dates, "P15-17-R3")
    mean = sum(candidate["samples"]) / max(len(candidate["samples"]), 1)
    candidate["mean_seconds"] = mean
    candidate["phase1_mean_seconds"] = PHASE1_MEAN_SECONDS
    candidate["target_mean_seconds"] = TARGET_MEAN_SECONDS
    candidate["gate_p90_at_most_5s"] = candidate["p90_seconds"] <= TARGET_P90_SECONDS
    candidate["gate_3x_vs_phase1"] = mean <= TARGET_MEAN_SECONDS
    candidate["resources"] = job_resource_record(wall_seconds=sum(candidate["samples"]))
    candidate["workers_cgroup"] = cgroup_worker_count()
    _write(ROOT / "THROUGHPUT.json", candidate)
    print(
        "candidate",
        "median",
        candidate["median_seconds"],
        "p90",
        candidate["p90_seconds"],
        "mean",
        mean,
        "p90_ok",
        candidate["gate_p90_at_most_5s"],
        "x3_ok",
        candidate["gate_3x_vs_phase1"],
    )

    rows = []
    for task_id, before_path in BEFORE_THROUGHPUT.items():
        before = json.loads(before_path.read_text())
        family, branch = PRIMARY_BRANCH[task_id]
        after = _family_plane(dates, family, branch)
        row = {
            "task_id": task_id,
            "family": family,
            "branch": branch,
            "comparable": False,
            "adapter_dual_scan_scope": "full account-day HistoricalFeatures plus dual B0/B0.1 adapter scan, single core",
            "adapter_dual_scan_median_seconds": before["median_seconds"],
            "adapter_dual_scan_p90_seconds": before["p90_seconds"],
            "adapter_dual_scan_path": str(before_path),
            "plane_scope": after["scope"],
            "plane_median_seconds": after["plane_median_seconds"],
            "plane_p90_seconds": after["plane_p90_seconds"],
            "note": "not a measurement of the family adapter scan; 04 dual-scan seconds are not comparable to the plane numbers",
        }
        rows.append(row)
        print(task_id, family, "dual_scan_p90", before["p90_seconds"], "plane_p90", after["plane_p90_seconds"])
    _write(
        ROOT / "FAMILY_THROUGHPUT.json",
        {
            "schema_version": "research-family-throughput-v2",
            "comparable": False,
            "note": "plane columns are account-day view plus applicable bank primitives on the new plane. They are not the family scan. Do not compute a per-family speedup against the 04 dual-scan numbers.",
            "dates": dates,
            "rows": rows,
        },
    )


if __name__ == "__main__":
    main()
