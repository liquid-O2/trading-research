#!/usr/bin/env python3
"""Historical volatility features and forward-RV targets on the quarter-hour
grid, for every requested account day (P2-03 inputs at grid times; no options,
no fitting).

Pass 1 (parallel, one account day per job, checkpointed as ``days/<day>.json``):
load the day's native NQ BBO midpoints once with the P2-03 loader, build the
minute frame, emit the grid rows (intraday features and forward targets) and
the day's summary. Pass 2 (parent): attach to each day's rows the day-level
inputs known at its open (HAR, Yang-Zhang 20, the 20-day Garman-Klass mean)
from the summaries of the sessions before it, and write one parquet per year
with a JSON summary that reconciles every requested day to a terminal
disposition: complete, non_trading_day, or failed with its reason.

    run_volatility_features.py --out <dir> [--start 2020-01-02] [--end YYYY-MM-DD]
        [--dates a,b] [--workers 3] [--limit N]

Nothing is fitted here. Days on or after 2026-04-01 are computed and flagged
``is_holdout`` so no later fit can use them by accident.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path



def last_day_on_disk() -> date:
    """The last calendar day the NQ one-minute archive reaches (a cheap proxy
    for the tape's end; the loader decides what each day actually holds)."""
    import pyarrow.parquet as pq

    folder = Path("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1m")
    year = max(int(p.stem) for p in folder.glob("*.parquet"))
    t = pq.read_table(folder / f"{year}.parquet", columns=["t"]).column("t").to_numpy()
    from datetime import datetime, timezone

    return datetime.fromtimestamp(int(t.max()) / 1000, tz=timezone.utc).date()


def weekdays(start: date, end: date) -> list[date]:
    out, day = [], start
    while day <= end:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def compute_one(text: str, out_dir: str) -> dict:
    """One account day: load, compute, checkpoint. Returns a small status."""
    import numpy as np

    from trading_research.research.experts.features import volatility_grid as vg
    from trading_research.research.experts.labels.volatility import load_bbo_midpoints
    from trading_research.research.rule_discovery.native import account_day_window, install_write_guard

    install_write_guard()
    started = time.monotonic()
    day = date.fromisoformat(text)
    target = Path(out_dir) / "days" / f"{text}.json"
    try:
        start, end = account_day_window(day)
        bbo = load_bbo_midpoints(day, start, end)
        loaded = time.monotonic()
        n = int(np.asarray(bbo["t_ns"]).size)
        if n == 0:
            doc = {"day": text, "disposition": "non_trading_day", "reason": "no_native_midpoints_in_the_account_day", "rows": [], "summary": None}
        else:
            result = vg.compute_day(day, bbo["t_ns"], bbo["mid"], bbo["available_at_ns"], instrument_id=str(bbo["instrument_id"]))
            doc = {"day": text, "disposition": "complete", "reason": None, "rows": result["rows"], "summary": result["summary"]}
        doc["seconds_load"] = round(loaded - started, 2)
        doc["seconds_total"] = round(time.monotonic() - started, 2)
        doc["peak_rss_bytes"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except Exception as exc:  # a failed day is a terminal disposition with its reason, never a silent gap
        doc = {"day": text, "disposition": "failed", "reason": f"{type(exc).__name__}: {exc}", "rows": [], "summary": None, "seconds_total": round(time.monotonic() - started, 2)}
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc))
    os.replace(tmp, target)
    return {k: doc.get(k) for k in ("day", "disposition", "reason", "seconds_load", "seconds_total", "peak_rss_bytes")} | {"n_rows": len(doc["rows"])}


def assemble(out: Path, days: list[date]) -> dict:
    import pandas as pd

    from trading_research.research.experts.features import volatility_grid as vg

    prior: list = []  # every requested day so far: a summary, None (no session), or a failed marker
    frames: dict[int, list[dict]] = {}
    dispositions = {}
    status_counts: dict[str, dict[str, int]] = {}
    for day in days:
        text = day.isoformat()
        path = out / "days" / f"{text}.json"
        if not path.is_file():
            dispositions[text] = {"disposition": "failed", "reason": "no_checkpoint_written"}
            prior.append({"day": text, "failed": True})
            continue
        doc = json.loads(path.read_text())
        dispositions[text] = {"disposition": doc["disposition"], "reason": doc.get("reason"), "n_rows": len(doc["rows"])}
        if doc["disposition"] == "complete":
            level = vg.day_level_inputs(prior)
            for row in doc["rows"]:
                frames.setdefault(day.year, []).append({**row, **level})
                for key, value in row.items():
                    if key.startswith("tgt_") and key.endswith("_status"):
                        status_counts.setdefault(key[:-7], {}).setdefault(value, 0)
                        status_counts[key[:-7]][value] += 1
            prior.append(doc["summary"])
        elif doc["disposition"] == "non_trading_day":
            prior.append(None)
        else:
            prior.append({"day": text, "failed": True})
    written = {}
    columns: list[str] = []
    for year, rows in sorted(frames.items()):
        frame = pd.DataFrame(rows)
        path = out / f"volatility_grid_{year}.parquet"
        frame.to_parquet(path, index=False)
        written[str(year)] = {"path": str(path), "rows": int(len(frame)), "days": int(frame["day"].nunique())}
        columns = list(frame.columns)
    counts: dict[str, int] = {}
    for d in dispositions.values():
        counts[d["disposition"]] = counts.get(d["disposition"], 0) + 1
    rows_written = sum(v["rows"] for v in written.values())
    rows_declared = sum(d.get("n_rows") or 0 for d in dispositions.values())
    summary = {
        "schema": vg.SCHEMA,
        "days_requested": len(days),
        "dispositions": counts,
        "reconciled": len(dispositions) == len(days) and rows_written == rows_declared,
        "rows_written": rows_written,
        "rows_declared_by_checkpoints": rows_declared,
        "target_status_counts": status_counts,
        "files": written,
        "columns": columns,
        "failures": [{"day": k, **v} for k, v in dispositions.items() if v["disposition"] == "failed"],
        "non_trading_days": [k for k, v in dispositions.items() if v["disposition"] == "non_trading_day"],
        "holdout_from": "2026-04-01",
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", default="2020-01-02")
    parser.add_argument("--end", default=None)
    parser.add_argument("--dates", default=None)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    if args.dates:
        days = sorted(date.fromisoformat(x) for x in args.dates.split(","))
    else:
        end = date.fromisoformat(args.end) if args.end else last_day_on_disk()
        days = weekdays(date.fromisoformat(args.start), end)
    if args.limit:
        days = days[: args.limit]
    (args.out / "days").mkdir(parents=True, exist_ok=True)
    todo = [d for d in days if not (args.out / "days" / f"{d.isoformat()}.json").is_file()]
    started = time.monotonic()
    print(json.dumps({"event": "start", "days": len(days), "todo": len(todo), "workers": args.workers}), flush=True)
    done = 0
    peak = 0
    seconds = []
    with ProcessPoolExecutor(max_workers=max(1, min(3, args.workers))) as pool:
        futures = {pool.submit(compute_one, d.isoformat(), str(args.out)): d for d in todo}
        for future in as_completed(futures):
            status = future.result()
            done += 1
            peak = max(peak, int(status.get("peak_rss_bytes") or 0))
            if status.get("seconds_total") is not None:
                seconds.append(float(status["seconds_total"]))
            if done % 25 == 0 or status["disposition"] == "failed":
                print(json.dumps({"event": "progress", "done": done, "of": len(todo), "elapsed_s": round(time.monotonic() - started, 1), "last": status}), flush=True)
    summary = assemble(args.out, days)
    summary_line = {k: summary[k] for k in ("days_requested", "dispositions", "reconciled", "rows_written")}
    print(json.dumps({"event": "complete", **summary_line, "wall_s": round(time.monotonic() - started, 1), "peak_rss_bytes_worker": peak, "seconds_per_day_mean": round(sum(seconds) / len(seconds), 2) if seconds else None}), flush=True)
    return 0 if summary["reconciled"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
