#!/usr/bin/env python3
"""A source adapter's mechanics over the whole tape on GENERATED structure, for
the families that expose ``scan_b02(market, rec)`` and had no population:
Saint (the composite balance and generated intraday lines), Member (prior
reaction areas and the composite's minor HVNs) and Keani (the open above
value, the imbalance break and its retest). Every branch of the family, the
passing episodes as the candidate pool, and the same one-position executed
list the other families use. Until 2026-09-18 these had replays of their dated
tickets at most, so no density, no pass rate and no upgrade could be judged.

    run_adapter_population.py --family saint|member|keani --out <dir>
        [--workers 4] [--dates a,b] [--limit N] [--scanner-overrides JSON]
        [--export-executed] [--export-candidates]

The pool is not restricted to the cash session: each scanner enforces its own
clocks on its episodes (Saint's one ticket is an Asia-session retest), and the
runner adds none. The executed-list policy is the study's convention, stated
in ``POLICY``; none of these sources prints a daily trade count.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import resource
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADAPTERS = {"saint": "saint", "member": "member", "keani": "keani"}
# one retest per broken level is his rule (TRAP pp.6-7) and the scanner already
# emits one; the rest is the study's convention, the same as the Sires list
POLICY = {"max_entries": 6, "max_per_line": 1, "allow_adds": False, "allow_flips": True, "reenter_same_line": False, "edge_first": False}


def _module(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _f(value):
    return None if value is None else float(Decimal(str(value)))


def scan_one(adapter: str, day: str, overrides: dict | None, export_executed: bool, export_candidates: bool) -> dict:
    import importlib

    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market
    from trading_research.research.rule_discovery.source_adapters.trade_selection import select_session_trades

    install_write_guard()
    pop = _module("run_jj_gb_population")
    rs = _module("replay_sires")
    started = time.monotonic()
    pop.apply_overrides(overrides)
    module = importlib.import_module(f"trading_research.research.rule_discovery.source_adapters.{adapter}")
    FAMILY = module.FAMILY
    market = load_source_market(day)
    document = module.scan_b02(market, {"family": FAMILY})
    episodes = document.get("episodes") or []
    counts = defaultdict(lambda: {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0})
    pool = []
    violations: list[dict] = []
    for ep in episodes:
        branch = str(ep.get("branch"))
        verdict = str(ep.get("research_verdict"))
        counts[branch]["episodes"] += 1
        counts[branch][verdict if verdict in ("pass", "fail", "unknown") else "unknown"] += 1
        if verdict != "pass":
            continue
        # no fact of a taken trade may be dated after its decision (2026-09-18: Member's
        # level was defined by bars after the trade, 93% wins); counted per session and
        # a population with any violation is not a result
        decided = int(ep.get("decision_at") or 0)
        late = [str(st.get("stage")) for st in ep.get("stages") or [] if st.get("at_ns") and int(st["at_ns"]) > decided]
        if late:
            violations.append({"session": day, "branch": branch, "decision_at": decided, "late_stages": late})
        geometry = ep.get("geometry") or {}
        values = dict(ep.get("values") or {})
        level = geometry.get("break_level") or values.get("reference_px") or values.get("level") or geometry.get("entry")
        # the line's identity for the one-opportunity key: its kind and price
        values.setdefault("reference_kind", f"{adapter}_level")
        values.setdefault("reference_px", level)
        values.setdefault("confirmation_mode", values.get("confirmation_mode") or "retest")
        values.setdefault("cycle", values.get("cycle") or 0)
        pool.append({**ep, "values": values, "candidate_id": f"{adapter}|{branch}|{ep.get('side')}|{level}|{ep.get('decision_at')}"})
    pool.sort(key=lambda ep: int(ep["decision_at"]))
    start_ns, end_ns = int(market.start), int(market.end)
    bars = rs.bars_between(market, start_ns, end_ns)
    executed = select_session_trades(pool, bars=bars, clock=(start_ns, end_ns), max_entries=POLICY["max_entries"], stop_after_target=False, reenter_same_line=POLICY["reenter_same_line"], allow_adds=POLICY["allow_adds"], max_per_line=POLICY["max_per_line"], allow_flips=POLICY["allow_flips"], edge_first=POLICY["edge_first"])
    stats = pop.executed_points(executed)
    stats["n_candidates"] = len(pool)
    out = {
        "date": day,
        "family": FAMILY,
        "seconds": round(time.monotonic() - started, 2),
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        "n_episodes": len(episodes),
        "counts": {k: dict(v) for k, v in counts.items()},
        "causality_violations": violations,
        "variants": {"B0.3": {FAMILY: stats}},
        "reads": {},
    }
    if export_executed:
        rows = []
        for item in (executed or {}).get("entries") or []:
            values = item.get("values") or {}
            rows.append({"family": FAMILY, "branch": item.get("branch"), "side": item.get("side"), "decision_at": int(item["decision_at"]), "entry": _f(item.get("entry")), "stop": _f(item.get("stop")), "target": _f(item.get("target")), "candidate_id": item.get("candidate_id"), "mode": item.get("confirmation_mode") or values.get("confirmation_mode"), "outcome_e0": item.get("outcome")})
        out["executed"] = rows
    if export_candidates:
        out["candidates"] = [{"branch": ep.get("branch"), "side": ep.get("side"), "decision_at": int(ep["decision_at"]), "candidate_id": ep["candidate_id"], "geometry": {k: _f(v) for k, v in (ep.get("geometry") or {}).items() if k in ("entry", "stop", "target", "break_level")}, "values": {k: v for k, v in (ep.get("values") or {}).items() if isinstance(v, (str, int, float, bool)) or v is None}} for ep in pool]
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=sorted(ADAPTERS), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dates", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--scanner-overrides", default=None, help="JSON {module.CONSTANT: value}, as run_jj_gb_population.py")
    parser.add_argument("--recycle", type=int, default=20, help="sessions a worker serves before it is replaced: the adapters cache prior-session windows per process and a long-lived Member worker grew to 9 GB (2026-09-18)")
    parser.add_argument("--skip-dates-file", type=Path, default=None, help="dates already finished by an earlier run of the same code (one per line); they are not re-run")
    parser.add_argument("--export-executed", action="store_true")
    parser.add_argument("--export-candidates", action="store_true")
    args = parser.parse_args(argv)
    pop = _module("run_jj_gb_population")
    overrides = None if not args.scanner_overrides else json.loads(args.scanner_overrides)
    if args.dates:
        dates = [item.strip() for item in args.dates.split(",") if item.strip()]
    else:
        # the same calendar the Jumbo/Green Bird and Sires populations run on
        from trading_research.research.method_pack import historical_runner as hr
        from trading_research.research.rule_discovery.baseline import PHASE1_RUN
        from trading_research.research.rule_discovery.run_baseline_repair import evaluation_dates

        registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
        dates = [str(d) for d in evaluation_dates(registry)]
    if args.skip_dates_file:
        finished = {d.strip() for d in args.skip_dates_file.read_text().split() if d.strip()}
        dates = [d for d in dates if d not in finished]
    if args.limit:
        dates = dates[: args.limit]
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    failures = []
    totals = {"sessions": 0, "net_points": 0.0, "trades": 0, "wins": 0, "losses": 0, "open": 0, "candidates": 0, "episodes": 0}
    branch_counts = defaultdict(lambda: {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0})
    peak = 0
    done = 0
    causality: list[dict] = []
    with (args.out / "rows.jsonl").open("w") as sink:
        with ProcessPoolExecutor(max_workers=max(1, args.workers), max_tasks_per_child=max(1, args.recycle)) as pool:
            futures = {pool.submit(scan_one, ADAPTERS[args.family], day, overrides, args.export_executed, args.export_candidates): day for day in dates}
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    failures.append({"date": day, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                done += 1
                sink.write(json.dumps({"kind": "session", **result}, default=str) + "\n")
                FAMILY = result["family"]
                stats = result["variants"]["B0.3"][FAMILY]
                totals["sessions"] += 1
                totals["net_points"] += stats["net_points"]
                totals["trades"] += stats["n_executed"]
                totals["wins"] += stats["wins"]
                totals["losses"] += stats["losses"]
                totals["open"] += stats["open"]
                totals["candidates"] += stats["n_candidates"]
                totals["episodes"] += result["n_episodes"]
                causality.extend(result.get("causality_violations") or [])
                peak = max(peak, int(result.get("peak_rss_bytes") or 0))
                for branch, c in result["counts"].items():
                    for k, v in c.items():
                        branch_counts[branch][k] += v
                if done % 25 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(dates), "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    n = max(1, totals["sessions"])
    summary = {
        "schema": "adapter-population-b03-v1",
        "family": args.family,
        "n_dates_requested": len(dates),
        "n_dates_complete": totals["sessions"],
        "failures": failures,
        "workers": args.workers,
        "wall_seconds": round(time.monotonic() - started, 1),
        "peak_rss_bytes_worker": peak,
        "causality_violations": len(causality),
        "causality_detail": causality[:50],
        "policy": POLICY,
        "scanner_overrides": overrides,
        "per_session": {"episodes": round(totals["episodes"] / n, 2), "candidates": round(totals["candidates"] / n, 2), "trades": round(totals["trades"] / n, 2), "net_points": round(totals["net_points"] / n, 3), "win_rate": round(totals["wins"] / max(1, totals["wins"] + totals["losses"]), 3), "open": totals["open"]},
        "branch_counts": {k: dict(v) for k, v in branch_counts.items()},
    }
    (args.out / "POPULATION.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    lines = [f"# Population, {args.family} mechanics on generated structure (B0.3)", "", f"- sessions: {totals['sessions']} of {len(dates)} (failures {len(failures)}); wall {summary['wall_seconds']}s; peak worker RSS {peak / 1e9:.2f} GB", "", "| episodes / session | candidates / session | trades / session | net points / session | win rate | open |", "| ---: | ---: | ---: | ---: | ---: | ---: |", f"| {summary['per_session']['episodes']} | {summary['per_session']['candidates']} | {summary['per_session']['trades']} | {summary['per_session']['net_points']} | {summary['per_session']['win_rate']} | {totals['open']} |", "", "| branch | episodes | pass | fail | unknown | pass rate |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for branch, c in sorted(branch_counts.items()):
        lines.append(f"| {branch} | {c['episodes']} | {c['pass']} | {c['fail']} | {c['unknown']} | {c['pass'] / max(1, c['episodes']):.4f} |")
    (args.out / "POPULATION.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"event": "population_complete", "dates": totals["sessions"], "failures": len(failures), "causality_violations": len(causality), "wall_s": summary["wall_seconds"]}))
    return 0 if not causality else 2


if __name__ == "__main__":
    raise SystemExit(main())
