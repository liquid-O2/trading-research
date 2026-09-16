"""17-worker wall per date, full pipeline through search_run.run_dates.

The BEFORE number is the sibling stage B run's own rate over exactly the window
this run occupies (its PROGRESS.json is sampled at the start and at the end), so
both engines are measured at 17 workers on the same machine under the same load.
"""
import json, time
from pathlib import Path

from trading_research.research.rule_discovery import search_run

ROOT = Path("/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-17")
SIBLING = Path(
    "/workspace/.worktrees/p15-17-stage-a/implementation/reports/research-work"
    "/P15-17/6cc3b4628129100d/attempt-0001/PROGRESS.json"
)
DATES = ["2020-01-02", "2020-06-01", "2020-11-02", "2021-01-04", "2021-06-01",
         "2021-11-01", "2022-01-03", "2022-06-01", "2022-11-01", "2023-01-03",
         "2023-06-01", "2023-11-06", "2024-01-02", "2024-06-03", "2024-11-01",
         "2025-01-02", "2025-06-02", "2025-11-03", "2026-01-02", "2026-06-01"]


def sibling() -> dict:
    return json.loads(SIBLING.read_text())


run_root = ROOT / "_fast/pipeline17/attempt-0001"
before = sibling()
started = time.perf_counter()
summary = search_run.run_dates(
    run_root=run_root,
    freeze_path=ROOT / "47dedaaa4f5b9ce1/FREEZE.json",
    dates=DATES,
    workers=17,
)
wall = time.perf_counter() - started
after = sibling()

d_dates = after["dates_done_this_process"] - before["dates_done_this_process"]
d_elapsed = after["elapsed_seconds"] - before["elapsed_seconds"]
row = {
    "schema": "p15-17-fast-pipeline17-v1",
    "dates": len(DATES),
    "workers": 17,
    "after_wall_seconds": wall,
    "after_seconds_per_date": wall / len(DATES),
    "after_dates_completed": summary["dates_completed"],
    "after_dates_failed": summary["dates_failed"],
    "before_source": str(SIBLING),
    "before_rate_seconds_per_date_cumulative": before["rate_seconds_per_date"],
    "before_rate_seconds_per_date_concurrent_window": (d_elapsed / d_dates) if d_dates else None,
    "before_window_dates": d_dates,
    "before_window_seconds": d_elapsed,
}
(ROOT / "_fast/PIPELINE17.json").write_text(json.dumps(row, indent=1, sort_keys=True))
print("PIPELINE17 " + json.dumps(row, sort_keys=True), flush=True)
