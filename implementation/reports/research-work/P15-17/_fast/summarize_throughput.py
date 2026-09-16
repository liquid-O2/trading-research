"""Fold throughput_raw.jsonl into THROUGHPUT_FAST.json and print the table."""
import json, statistics
from pathlib import Path

F = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (F / "throughput_raw.jsonl").read_text().splitlines() if l.strip()]
COMPONENTS = ("load", "market_open", "data_plane", "prepay", "tape_compaction",
              "whole_bank", "stage_b_overhead", "end_to_end")

def p90(values):
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    k = 0.9 * (len(values) - 1)
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)

per_date = {}
for row in rows:
    per_date.setdefault(row["date"], {}).setdefault(row["tag"], []).append(row)
dates = sorted(d for d, v in per_date.items() if {"BEFORE", "AFTER"} <= set(v))
out = {
    "schema": "p15-17-fast-throughput-v1",
    "protocol": ("single core (taskset -c 100), one process per session, fresh per session, "
                 "the 20 THROUGHPUT_B02 dates, BEFORE = worktree p15-17-stage-a at 456d0812, "
                 "AFTER = worktree p15-17-fast, interleaved before-after-before-after per date; "
                 "the machine also carries the 17-worker stage B run throughout"),
    "dates": dates,
    "reps_per_date_per_engine": 2,
    "components": {},
    "per_date": {},
}
for tag in ("BEFORE", "AFTER"):
    for comp in COMPONENTS:
        series = [statistics.median([r[comp] for r in per_date[d][tag]]) for d in dates]
        out["per_date"].setdefault(tag, {})[comp] = series
for comp in COMPONENTS:
    b = out["per_date"]["BEFORE"][comp]
    a = out["per_date"]["AFTER"][comp]
    mb, ma = statistics.median(b), statistics.median(a)
    pb, pa = p90(b), p90(a)
    out["components"][comp] = {
        "before_median_seconds": mb, "after_median_seconds": ma,
        "before_p90_seconds": pb, "after_p90_seconds": pa,
        "median_speedup": (mb / ma) if ma else None,
        "p90_speedup": (pb / pa) if pa else None,
    }
(F / "THROUGHPUT_FAST.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print(f"dates={len(dates)}")
print(f"{'component':<18}{'before med':>11}{'after med':>11}{'x':>7}{'before p90':>12}{'after p90':>11}{'x':>7}")
for comp in COMPONENTS:
    c = out["components"][comp]
    print(f"{comp:<18}{c['before_median_seconds']:>11.2f}{c['after_median_seconds']:>11.2f}"
          f"{(c['median_speedup'] or 0):>7.1f}{c['before_p90_seconds']:>12.2f}"
          f"{c['after_p90_seconds']:>11.2f}{(c['p90_speedup'] or 0):>7.1f}")
