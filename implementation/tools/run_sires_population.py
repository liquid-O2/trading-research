#!/usr/bin/env python3
"""Population run for the order-level families on generated boxes (Sires and
Saint mechanics): every session of the frozen list, the aggression boxes alive
at each minute (from the box table of sires_box_table.py: formed within the
lookback, not yet consumed), every fill the one-minute mechanics admit at
every alive box on both sides, then the family's executed list (one position
at a time, adds on the same line, flips) and its result in points.

The objective of a fill is the near edge of the nearest alive box beyond the
entry in the trade's direction (Sires trades level to level); when no box
lies within OBJECTIVE_MAX_POINTS the fill has no objective and is not traded.

Selection variants (JSON list of {name, overrides}) are evaluated on the same
candidate list; B0.3 is always included. Output: rows.jsonl (one session line
per session with every variant's result and the candidate count) and
POPULATION.json / POPULATION.md.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[1]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

NS = 1_000_000_000
MINUTE = 60 * NS
LOOKBACK_DAYS = 14
OBJECTIVE_MAX_POINTS = Decimal("150")
MIN_RR = Decimal("1")
SESSION = ("09:30", "16:00")
POLICY = {"max_entries": 6, "max_per_line": 2, "allow_adds": "same_line", "allow_flips": True, "reenter_same_line": True, "edge_first": False}


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _d(value):
    return None if value is None else Decimal(str(value))


def alive_boxes(table, session_open: int, session_end: int) -> list[dict]:
    """Boxes formed within the lookback and not consumed before the session opens."""
    lo_t = session_open - LOOKBACK_DAYS * 86400 * NS
    sub = table[(table["known_at"] >= lo_t) & (table["known_at"] < session_end)]
    out = []
    for row in sub.itertuples(index=False):
        consumed = None if row.consumed_at is None or row.consumed_at != row.consumed_at else int(row.consumed_at)
        if consumed is not None and consumed < session_open and int(row.known_at) < session_open:
            continue  # carried in and already consumed
        out.append({"id": f"box:{int(row.known_at)}:{row.lo}:{row.hi}", "known_at": int(row.known_at), "consumed_at": consumed, "lo": _d(row.lo), "hi": _d(row.hi), "n_orders": int(row.n_orders), "contracts": int(row.contracts), "sides": row.sides})
    return out


def objective_for(boxes: list[dict], entry: Decimal, side: str, at_ns: int) -> Decimal | None:
    best = None
    for box in boxes:
        if box["known_at"] >= at_ns:
            continue
        if side == "long":
            edge = box["lo"]
            if edge > entry and edge - entry <= OBJECTIVE_MAX_POINTS and (best is None or edge < best):
                best = edge
        else:
            edge = box["hi"]
            if edge < entry and entry - edge <= OBJECTIVE_MAX_POINTS and (best is None or edge > best):
                best = edge
    return best


def scan_one(day: str, table_path: str, variants: list[dict]) -> dict:
    from trading_research.research.method_pack import historical_runner as hr
    from trading_research.research.method_pack.historical_features import HistoricalFeatures
    from trading_research.research.rule_discovery.baseline import PHASE1_RUN
    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters.trade_selection import select_session_trades

    import pandas as pd

    global _RECORDS, _TABLE, _RS, _POP
    try:
        records = _RECORDS
    except NameError:
        install_write_guard()
        registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
        records = _RECORDS = hr._records(registry)
        _TABLE = pd.read_parquet(table_path)
        _RS = _module("replay_sires")
        _POP = _module("run_jj_gb_population")
    started = time.monotonic()
    market = HistoricalFeatures(day, records=records)
    open_ns, end_ns = int(market.at(SESSION[0])), int(market.at(SESSION[1]))
    session_open = int(market.start)
    rows = _RS.bars_between(market, session_open, end_ns)
    boxes = alive_boxes(_TABLE, session_open, end_ns)
    pool = []
    for box in boxes:
        for side in ("long", "short"):
            lo, hi = box["lo"], box["hi"]
            line = hi if side == "short" else lo
            fills = []
            for cycle in _RS.sweep_fail_cycles(rows, line, side):
                for fill in _RS.fills_after_failure(rows, cycle, line, side, box_low=lo, box_high=hi):
                    fills.append({**fill, "play": "failure", "cycle": cycle["cycle"], "level_px": line})
            near = hi if side == "long" else lo
            for fill in _RS.defended_band_fills(rows, lo, hi, side):
                fills.append({**fill, "play": "defence", "cycle": 0, "level_px": near})
            for fill in _RS.reclaim_fills(rows, lo, hi, side):
                fills.append({**fill, "play": "reclaim", "cycle": 0, "level_px": near})
            for fill in _RS.break_stop_fills(rows, near, side):
                fills.append({**fill, "play": "break", "cycle": 0, "level_px": near})
            for fill in fills:
                at = int(fill["at"])
                if at <= box["known_at"] or at < open_ns or at >= end_ns:
                    continue
                if box["consumed_at"] is not None and at > box["consumed_at"] and box["known_at"] < session_open:
                    continue
                entry, stop = _d(fill["entry"]), _d(fill.get("stop"))
                if entry is None or stop is None or entry == stop:
                    continue
                target = objective_for(boxes, entry, side, at)
                if target is None or abs(target - entry) / abs(entry - stop) < MIN_RR:
                    continue
                pool.append(
                    {
                        "research_verdict": "pass",
                        "branch": fill["play"],
                        "side": side,
                        "decision_at": at,
                        "candidate_id": f"{box['id']}|{side}|{fill['play']}|{fill['mode']}|{at}",
                        "values": {"cycle": fill.get("cycle"), "reference_px": fill["level_px"], "confirmation_mode": fill["mode"], "reference_kind": "aggression_box", "segment": "ny"},
                        "reference": {"id": box["id"]},
                        "geometry": {"entry": entry, "stop": stop, "target": target},
                    }
                )
    pool.sort(key=lambda ep: ep["decision_at"])
    results = {}
    for variant in [{"name": "B0.3", "overrides": {}}] + list(variants):
        policy = {**POLICY, **{k.split(".", 1)[1]: v for k, v in (variant.get("overrides") or {}).items() if k.startswith("policy.")}}
        executed = select_session_trades(pool, bars=rows, clock=(open_ns, end_ns), max_entries=policy["max_entries"], stop_after_target=False, reenter_same_line=policy["reenter_same_line"], allow_adds=policy["allow_adds"], max_per_line=policy["max_per_line"], allow_flips=policy["allow_flips"], edge_first=policy["edge_first"])
        stats = _POP.executed_points(executed)
        stats["n_candidates"] = len(pool)
        results[variant["name"]] = {"SIRES": stats}
    return {"date": day, "seconds": round(time.monotonic() - started, 2), "n_boxes": len(boxes), "n_candidates": len(pool), "variants": results, "reads": {}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--boxes", type=Path, required=True, help="boxes.parquet from sires_box_table.py")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--dates", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--selection-variants", type=Path, default=None)
    args = parser.parse_args(argv)
    from trading_research.research.method_pack import historical_runner as hr
    from trading_research.research.rule_discovery.baseline import PHASE1_RUN
    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.run_baseline_repair import evaluation_dates

    install_write_guard()
    registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
    calendar = list(evaluation_dates(registry))
    if args.dates and args.dates.startswith("every:"):
        step = int(args.dates.split(":", 1)[1])
        dates = calendar[::step]
    elif args.dates:
        dates = args.dates.split(",")
    else:
        dates = calendar
    if args.limit:
        dates = dates[: args.limit]
    variants = json.loads(args.selection_variants.read_text()) if args.selection_variants else []
    args.out.mkdir(parents=True, exist_ok=True)
    totals = defaultdict(lambda: {"sessions": 0, "net_points": 0.0, "trades": 0, "round_trips": 0, "wins": 0, "losses": 0, "open": 0, "candidates": 0})
    failures = []
    started = time.monotonic()
    with (args.out / "rows.jsonl").open("w") as sink:
        with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(scan_one, day, str(args.boxes), variants): day for day in dates}
            done = 0
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    failures.append({"date": day, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                done += 1
                sink.write(json.dumps({"kind": "session", **result}, default=str) + "\n")
                for name, per_family in result["variants"].items():
                    for family, stats in per_family.items():
                        agg = totals[(name, family)]
                        agg["sessions"] += 1
                        agg["net_points"] += stats["net_points"]
                        agg["trades"] += stats["n_executed"]
                        agg["round_trips"] += stats["n_round_trips"]
                        agg["wins"] += stats["wins"]
                        agg["losses"] += stats["losses"]
                        agg["open"] += stats["open"]
                        agg["candidates"] += stats["n_candidates"]
                if done % 50 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(dates), "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    summary = {
        "schema": "sires-population-b03-v1", "n_dates_requested": len(dates), "n_dates_complete": done, "failures": failures, "wall_seconds": round(time.monotonic() - started, 1), "lookback_days": LOOKBACK_DAYS, "policy": POLICY,
        "variants": {f"{name}|{family}": {**agg, "net_points": round(agg["net_points"], 2), "net_points_per_session": round(agg["net_points"] / agg["sessions"], 3) if agg["sessions"] else None, "trades_per_session": round(agg["trades"] / agg["sessions"], 2) if agg["sessions"] else None, "candidates_per_session": round(agg["candidates"] / agg["sessions"], 1) if agg["sessions"] else None, "win_rate": round(agg["wins"] / (agg["wins"] + agg["losses"]), 3) if (agg["wins"] + agg["losses"]) else None} for (name, family), agg in sorted(totals.items())},
    }
    (args.out / "POPULATION.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    lines = ["# Population, Sires mechanics on generated aggression boxes (B0.3)", "", f"- sessions: {done} of {len(dates)} (failures {len(failures)}); wall {summary['wall_seconds']}s", "", "| variant | family | sessions | candidates / session | net points / session | trades / session | win rate | open |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for key, agg in summary["variants"].items():
        name, family = key.split("|", 1)
        lines.append(f"| {name} | {family} | {agg['sessions']} | {agg['candidates_per_session']} | {agg['net_points_per_session']} | {agg['trades_per_session']} | {agg['win_rate']} | {agg['open']} |")
    (args.out / "POPULATION.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"event": "population_complete", "dates": done, "wall_s": summary["wall_seconds"], "failures": len(failures)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
