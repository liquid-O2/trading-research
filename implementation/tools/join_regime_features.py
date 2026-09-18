#!/usr/bin/env python3
"""Attach the volatility regime known at a decision to every row of a
population: the latest quarter-hour grid row of the same account day whose
issue time is at or before the row's ``decision_at`` (the grid row itself uses
nothing after its issue time), as named ``vol_`` features. Only the feature
columns of the grid are read; its forward targets are never joined.

Adds two relative reads a trader would make of them: how the last hour's
realized variance stands against the prior day's and against the 22-day level
(is this an expansive or a compressed moment for this market), and how large
the overnight range was for the opening.

    join_regime_features.py --rows rows.jsonl --grid-dir <dir with volatility_grid_<year>.parquet> --out rows_regime.jsonl
"""
from __future__ import annotations

import argparse
import json
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path

FEATURES = (
    "log_rv_recent_5m",
    "log_rv_recent_15m",
    "log_rv_recent_60m",
    "log_gk_15m",
    "log_gk_60m",
    "rth_range_so_far_over_spot",
    "overnight_range_over_open",
    "log_overnight_rv_cov",
    "har_rth_har1",
    "har_rth_har5",
    "har_rth_har22",
    "log_yz20_rth",
    "log_gk20_mean_rth",
    "log_gk_prior_day_rth",
)
STATUS = {"log_rv_recent_5m": "rv_recent_5m_status", "log_rv_recent_15m": "rv_recent_15m_status", "log_rv_recent_60m": "rv_recent_60m_status", "log_gk_15m": "gk_15m_status", "log_gk_60m": "gk_60m_status"}


def load_grid(grid_dir: Path, years: set[str]):
    import pyarrow.parquet as pq

    per_day: dict[str, tuple[list[int], list[dict]]] = {}
    wanted = ["day", "issue_ns", *FEATURES, *sorted(set(STATUS.values()))]
    for year in sorted(years):
        path = grid_dir / f"volatility_grid_{year}.parquet"
        if not path.is_file():
            continue
        table = pq.read_table(path, columns=wanted).to_pylist()
        bucket = defaultdict(list)
        for row in table:
            bucket[str(row["day"])[:10]].append(row)
        for day, rows in bucket.items():
            rows.sort(key=lambda r: int(r["issue_ns"]))
            per_day[day] = ([int(r["issue_ns"]) for r in rows], rows)
    return per_day


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--grid-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    rows = [json.loads(line) for line in args.rows.open()]
    events = [r for r in rows if r.get("kind") != "session" and r.get("decision_at") is not None]
    grid = load_grid(args.grid_dir, {str(r["session"])[:4] for r in events})
    joined = missing = 0
    with args.out.open("w") as sink:
        for r in events:
            day = str(r["session"])[:10]
            stamps, grows = grid.get(day, ([], []))
            k = bisect_right(stamps, int(r["decision_at"])) - 1
            if k < 0:
                missing += 1
                for f in FEATURES:
                    r[f"vol_{f}"] = None
            else:
                g = grows[k]
                joined += 1
                for f in FEATURES:
                    ok = STATUS.get(f) is None or g.get(STATUS[f]) == "ok"
                    r[f"vol_{f}"] = None if not ok or g.get(f) is None else float(g[f])
                r["vol_grid_age_minutes"] = round((int(r["decision_at"]) - stamps[k]) / 6e10, 1)
            hour, prior, level = r.get("vol_log_rv_recent_60m"), r.get("vol_har_rth_har1"), r.get("vol_har_rth_har22")
            # log ratios: the last hour's variance rate against a day's. The grid's hour is a 60-minute
            # sum and the HAR terms are whole cash sessions (390 minutes), so put the hour on the day's scale first
            import math

            scaled = None if hour is None else hour + math.log(6.5)
            r["vol_hour_vs_prior_day"] = None if scaled is None or prior is None else round(scaled - prior, 4)
            r["vol_hour_vs_22day"] = None if scaled is None or level is None else round(scaled - level, 4)
            r["vol_prior_day_vs_22day"] = None if prior is None or level is None else round(prior - level, 4)
            sink.write(json.dumps(r) + "\n")
    print(json.dumps({"event": "joined", "rows": len(events), "joined": joined, "no_grid_row": missing, "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
