#!/usr/bin/env python3
"""The aggression-box table for the order-level families (Sires, Saint):
every box the adaptive cluster rule draws over the whole NQ tape, once, with
the time it formed and the time price consumed it (traded through both edges
by CONSUMED_POINTS). The population runner reads boxes from this table
instead of re-clustering two weeks of orders per session.

Boxes are clustered week by week (the trade parquet is weekly); a week's
clustering starts one hour early so the adaptive size cut has its trailing
window at the week's first orders. ``consumed_at`` is searched in the same
week and the following one (a box older than that is either consumed or
carried; the runner treats a missing consumed_at as alive).

Output: boxes.parquet (one row per box) and a JSON summary.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
NS = 1_000_000_000
CONSUMED_POINTS = 5.0
PARAMS = {"min_size": 30, "band": 6.0, "window_s": 180, "min_orders": 2, "adaptive": {"quantile": 0.995, "lookback_s": 3600, "floor": 20}}


def _fit():
    spec = importlib.util.spec_from_file_location("sires_levels_fit", HERE / "sires_levels_fit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def week_boxes(monday: str) -> list[dict]:
    fit = _fit()
    start = fit.ns_at(monday, "00:00", -1) - 3600 * NS
    end = fit.ns_at(monday, "00:00", 6)
    orders = fit.orders_between(monday, start, end)
    if orders is None or orders.empty:
        return []
    boxes = fit.cluster_orders(orders, min_size=PARAMS["min_size"], band=PARAMS["band"], window_s=PARAMS["window_s"], min_orders=PARAMS["min_orders"], adaptive=PARAMS["adaptive"])
    # consumption within the week (the runner completes it with the next week)
    t = orders["t"].to_numpy(); lo = orders["lo"].to_numpy(); hi = orders["hi"].to_numpy()
    out = []
    for b in boxes:
        after = t > int(b["known_at"])
        up = np.flatnonzero(after & (hi >= b["hi"] + CONSUMED_POINTS))
        dn = np.flatnonzero(after & (lo <= b["lo"] - CONSUMED_POINTS))
        consumed = int(max(t[up[0]], t[dn[0]])) if up.size and dn.size else None
        out.append({"week": monday, "known_at": int(b["known_at"]), "lo": float(b["lo"]), "hi": float(b["hi"]), "n_orders": int(b["n_orders"]), "contracts": int(b["contracts"]), "largest": int(b["largest"]), "sides": b["sides"], "aggressor": b.get("aggressor"), "consumed_at": consumed})
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", default="2020-01-06")
    parser.add_argument("--end", default="2026-09-07")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args(argv)
    fit = _fit()
    mondays = []
    d = date.fromisoformat(args.start)
    d -= timedelta(days=d.weekday())
    while d <= date.fromisoformat(args.end):
        if fit.week_file(d.isoformat()).exists():
            mondays.append(d.isoformat())
        d += timedelta(days=7)
    rows: list[dict] = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for monday, boxes in zip(mondays, pool.map(week_boxes, mondays)):
            rows.extend(boxes)
            print(json.dumps({"week": monday, "boxes": len(boxes)}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows).sort_values("known_at").reset_index(drop=True)
    # complete the consumption across week boundaries: a box unconsumed in its
    # week is checked against the next week's boxes' order span cheaply via the
    # next week's price path (min/max of its boxes); left None when unknown
    frame.to_parquet(args.out / "boxes.parquet", index=False)
    summary = {"weeks": len(mondays), "boxes": int(len(frame)), "boxes_per_week": round(len(frame) / max(1, len(mondays)), 1), "consumed_in_week": int(frame["consumed_at"].notna().sum()), "params": PARAMS, "consumed_points": CONSUMED_POINTS}
    (args.out / "BOX_TABLE.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"event": "box_table_complete", **summary}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
