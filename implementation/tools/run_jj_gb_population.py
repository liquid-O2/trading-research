#!/usr/bin/env python3
"""Population run for the source-faithful Jumbo and Green Bird scans (B0.3).

Runs the same session list P15-16A used (the frozen P15-00 classified list,
n=1742) through the rebuilt scanners and writes, per branch and per family:
the episode / pass / fail counts, the day-read classification counts, entries
per session from the selection layer, and the stop-distance and R:R
distributions the plausibility section is judged against.

Per-session rows go to rows.jsonl (one compact line per episode that reached a
risk-defined entry, plus one line per session for the selection); the summary
goes to POPULATION.json and POPULATION.md.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

FAMILIES = ("JJ-TBR", "GB-FAIL", "GB-VWAP", "GB-SCALP")


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _f(value):
    if value is None:
        return None
    return float(value)


MODULES = ("jumbo", "green_b02", "trade_selection")


def apply_overrides(overrides: dict | None) -> dict:
    """Set ``module.CONSTANT`` values on the adapter modules; return the
    previous values so they can be restored."""
    from trading_research.research.rule_discovery.source_adapters import green_b02, jumbo, trade_selection

    modules = {"jumbo": jumbo, "green_b02": green_b02, "trade_selection": trade_selection}
    previous = {}
    for key, value in (overrides or {}).items():
        module_name, _, name = key.partition(".")
        module = modules[module_name]
        if not hasattr(module, name):
            raise KeyError(f"unknown override {key}")
        current = getattr(module, name)
        previous[key] = current
        # coerce to the constant's own type: Decimals arrive as strings in
        # JSON, windows as lists
        if isinstance(current, Decimal) and not isinstance(value, Decimal):
            value = Decimal(str(value))
        elif isinstance(current, tuple) and isinstance(value, list):
            value = tuple(value)
        setattr(module, name, value)
    return previous


def executed_points(executed: dict) -> dict:
    """The executed list's result in points a contract: a target pays its
    reward, a stop (or an ambiguous bar) costs its stop distance, an open
    position at the end of the bars pays nothing."""
    out = {"n_executed": int(executed.get("n_entries") or 0), "n_round_trips": int(executed.get("n_round_trips") or 0), "net_points": 0.0, "wins": 0, "losses": 0, "open": 0, "ambiguous": 0}
    for item in executed.get("entries") or []:
        outcome = item.get("outcome")
        if outcome == "target":
            out["net_points"] += float(item.get("reward_points") or 0)
            out["wins"] += 1
        elif outcome in ("stop", "ambiguous"):
            out["net_points"] -= float(item.get("stop_points") or 0)
            out["losses"] += 1
            if outcome == "ambiguous":
                out["ambiguous"] += 1
        else:
            out["open"] += 1
    out["net_points"] = round(out["net_points"], 2)
    return out


def scan_one(day: str, sessionstat: bool, scanner_overrides: dict | None = None, selection_variants: list | None = None, export_executed: bool = False) -> dict:
    from trading_research.research.method_pack import historical_runner as hr
    from trading_research.research.method_pack.historical_features import HistoricalFeatures
    from trading_research.research.rule_discovery.baseline import PHASE1_RUN
    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
    from trading_research.research.rule_discovery.source_adapters import jumbo as jj

    global _RECORDS
    try:
        records = _RECORDS
    except NameError:
        install_write_guard()
        registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
        records = _RECORDS = hr._records(registry)

    started = time.monotonic()
    apply_overrides(scanner_overrides)  # a rescan candidate: the whole worker runs with it
    market = HistoricalFeatures(day, records=records)
    market.jj_sessionstat = bool(sessionstat)
    loaded = time.monotonic()
    documents = {"JJ-TBR": jj.scan_b02(market, {"branch": "all"})}
    for family in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
        documents[family] = gb.scan_b02(market, {"family": family, "branch": "all"})
    # selection variants: the same passing episodes through the family's own
    # selection with a different executed-list policy; cheap beside the scan
    variants: dict = {}
    for variant in selection_variants or []:
        previous = apply_overrides(variant.get("overrides"))
        try:
            per_family = {}
            for family, document in documents.items():
                passing = [ep for ep in document.get("episodes") or [] if ep.get("research_verdict") == "pass"]
                if family == "JJ-TBR":
                    read = document.get("day_read") or {}
                    selection = jj.selection_for(market, passing, primary_play=read.get("primary_play"))
                else:
                    selection = gb.selection_for(market, passing)
                per_family[family] = executed_points(selection.get("executed") or {})
                per_family[family]["n_candidates"] = int(selection.get("n_entries") or 0)
            variants[variant["name"]] = per_family
            if variant["name"] == "B0.3" and export_executed:
                executed_rows = []
                for family, document in documents.items():
                    passing = [ep for ep in document.get("episodes") or [] if ep.get("research_verdict") == "pass"]
                    selection = jj.selection_for(market, passing, primary_play=(document.get("day_read") or {}).get("primary_play")) if family == "JJ-TBR" else gb.selection_for(market, passing)
                    for item in (selection.get("executed") or {}).get("entries") or []:
                        executed_rows.append({"family": family, "branch": item.get("branch"), "side": item.get("side"), "decision_at": int(item["decision_at"]), "entry": _f(item.get("entry")), "stop": _f(item.get("stop")), "target": _f(item.get("target")), "candidate_id": item.get("candidate_id"), "mode": item.get("confirmation_mode"), "outcome_e0": item.get("outcome")})
                variants["__executed__"] = executed_rows
        finally:
            apply_overrides(previous)

    rows = []
    counts = defaultdict(lambda: {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0})
    opportunities = defaultdict(set)
    selection = {}
    reads = {}
    causality_violations = 0
    causality_rows: list[dict] = []
    for family, document in documents.items():
        reads[family] = document.get("day_read")
        selection[family] = {
            "n_entries": (document.get("selection") or {}).get("n_entries", 0),
            # the candidate list (every admitted opportunity once) is n_entries;
            # the executed list (one position at a time, adds, flips) beside it
            "n_executed": ((document.get("selection") or {}).get("executed") or {}).get("n_entries", 0),
            "n_round_trips": ((document.get("selection") or {}).get("executed") or {}).get("n_round_trips", 0),
            "n_candidates": (document.get("selection") or {}).get("n_candidates", 0),
            "primary_play": (document.get("selection") or {}).get("primary_play"),
            "fallback_play_used": (document.get("selection") or {}).get("fallback_play_used"),
            "entries": [
                {
                    "branch": item["branch"],
                    "side": item["side"],
                    "decision_at": item["decision_at"],
                    "stop_points": _f(item["stop_points"]),
                    "r_multiple_at_target": _f(item["r_multiple_at_target"]),
                    "outcome": item["outcome"],
                }
                for item in (document.get("selection") or {}).get("entries", [])
            ],
        }
        for episode in document.get("episodes") or []:
            branch = episode.get("branch")
            key = (family, branch)
            counts[key]["episodes"] += 1
            counts[key][episode["research_verdict"]] += 1
            stamps = [int(row["at_ns"]) for row in episode.get("stages") or [] if row.get("at_ns") is not None]
            if stamps and episode.get("decision_at") is not None and int(episode["decision_at"]) < max(stamps):
                causality_violations += 1
                latest = max((row for row in episode.get("stages") or [] if row.get("at_ns") is not None), key=lambda row: int(row["at_ns"]))
                causality_rows.append({"family": family, "branch": branch, "candidate_id": episode.get("candidate_id"), "verdict": episode["research_verdict"], "decision_at": int(episode["decision_at"]), "latest_stage": latest.get("stage"), "latest_at": int(latest["at_ns"]), "mode": (episode.get("values") or {}).get("confirmation_mode")})
            if episode["research_verdict"] != "pass":
                continue
            values_now = episode.get("values") or {}
            opportunities[key].add(
                (episode.get("side"), values_now.get("reference_kind"), values_now.get("level_edge"), values_now.get("cycle"))
            )
            geometry = episode.get("geometry") or {}
            values = episode.get("values") or {}
            rows.append(
                {
                    "date": day,
                    "family": family,
                    "branch": branch,
                    "play": values.get("play"),
                    "side": episode.get("side"),
                    "mode": values.get("confirmation_mode"),
                    "reference": values.get("reference_kind"),
                    "decision_at": episode.get("decision_at"),
                    "entry": _f(geometry.get("entry")),
                    "stop": _f(geometry.get("stop")),
                    "target": _f(geometry.get("target")),
                    "stop_points": _f(geometry.get("stop_points")),
                    "reward_points": _f(geometry.get("reward_points")),
                    "rr": _f(geometry.get("r_multiple_at_target")),
                    # the opportunity identity, so selection policies can be
                    # re-run offline on these rows (Phase 1.5 rebuilt plan)
                    "candidate_id": episode.get("candidate_id"),
                    "reference_id": (episode.get("reference") or {}).get("id"),
                    "reference_px": _f(values.get("reference_px")),
                    "level_edge": values.get("level_edge"),
                    "cycle": values.get("cycle"),
                    "segment": values.get("segment"),
                }
            )
    return {
        "date": day,
        "rows": rows,
        "variants": variants,
        "counts": {f"{family}|{branch}": dict(value) for (family, branch), value in counts.items()},
        "opportunities": {f"{family}|{branch}": len(value) for (family, branch), value in opportunities.items()},
        "selection": selection,
        "reads": {
            "JJ-TBR": None if not reads.get("JJ-TBR") else {
                "classification": reads["JJ-TBR"].get("classification"),
                "primary_play": reads["JJ-TBR"].get("primary_play"),
                "plays": reads["JJ-TBR"].get("plays"),
                "range_bin": (reads["JJ-TBR"].get("inputs") or {}).get("range_bin"),
                "open_location": (reads["JJ-TBR"].get("inputs") or {}).get("open_location"),
            },
            "GB-FAIL": None if not reads.get("GB-FAIL") else {
                "day_model": reads["GB-FAIL"].get("day_model"),
                "primary_play": reads["GB-FAIL"].get("primary_play"),
                "bias": reads["GB-FAIL"].get("bias"),
                "events": reads["GB-FAIL"].get("overnight_events"),
            },
        },
        "omissions": {family: list(document.get("omissions") or []) for family, document in documents.items()},
        "causality_violations": causality_violations,
        "causality_rows": causality_rows,
        "load_seconds": loaded - started,
        "scan_seconds": time.monotonic() - loaded,
        "peak_rss_bytes": peak_rss_bytes(),
    }


def _quantiles(values: list[float]) -> dict:
    if not values:
        return {}
    ordered = sorted(values)

    def q(p):
        index = min(len(ordered) - 1, max(0, int(round(p * (len(ordered) - 1)))))
        return ordered[index]

    return {"n": len(ordered), "min": ordered[0], "p25": q(0.25), "median": q(0.5), "p75": q(0.75), "p90": q(0.9), "max": ordered[-1]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--dates", default=None, help="comma-separated dates, or a slice like 'every:87'")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sessionstat", action="store_true", help="compute the SessionStat envelope (60 prior windows per session)")
    parser.add_argument("--scanner-overrides", default=None, help='JSON: {"jumbo.JUDAS_RAID_WINDOW": ["09:00","10:30"], ...} (a rescan candidate)')
    parser.add_argument("--selection-variants", type=Path, default=None, help="JSON list of {name, overrides} evaluated on the same scan (selection candidates); B0.3 is always added")
    parser.add_argument("--export-executed", action="store_true", help="write the B0.3 executed entries of each session into the session line (for the exit-policy study)")
    args = parser.parse_args(argv)
    scanner_overrides = json.loads(args.scanner_overrides) if args.scanner_overrides else None
    selection_variants = [{"name": "B0.3", "overrides": {}}]
    if args.selection_variants:
        selection_variants += json.loads(args.selection_variants.read_text())

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
        dates = [item.strip() for item in args.dates.split(",") if item.strip()]
    else:
        dates = calendar
    if args.limit:
        dates = dates[: args.limit]

    args.out.mkdir(parents=True, exist_ok=True)
    rows_path = args.out / "rows.jsonl"
    started = time.monotonic()
    totals = defaultdict(lambda: {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0})
    entries_per_session = defaultdict(list)
    executed_per_session = defaultdict(list)
    round_trips_per_session = defaultdict(list)
    stop_points = defaultdict(list)
    rr = defaultdict(list)
    outcomes = defaultdict(Counter)
    classification = Counter()
    day_model = Counter()
    primary_play = defaultdict(Counter)
    range_bins = Counter()
    open_locations = Counter()
    causality = 0
    causality_detail: list[dict] = []
    variant_totals: dict = defaultdict(lambda: {"sessions": 0, "net_points": 0.0, "trades": 0, "round_trips": 0, "wins": 0, "losses": 0, "open": 0})
    omission_totals: Counter = Counter()
    scan_errors: list[dict] = []
    opportunity_totals = Counter()
    failures = []
    peak = 0
    per_date_seconds = []

    # Contiguous chunks so each worker's prior-session cache warms.
    chunks = [dates[i::args.workers] for i in range(args.workers)] if args.workers > 1 else [dates]
    chunks = [chunk for chunk in chunks if chunk]

    with rows_path.open("w") as sink:
        with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(scan_one, day, args.sessionstat, scanner_overrides, selection_variants, args.export_executed): day for day in dates}
            done = 0
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception as exc:  # infrastructure failure, never a silent pass
                    failures.append({"date": day, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                done += 1
                per_date_seconds.append(result["load_seconds"] + result["scan_seconds"])
                peak = max(peak, result["peak_rss_bytes"])
                causality += result["causality_violations"]
                for row in result.get("causality_rows") or []:
                    if len(causality_detail) < 200:
                        causality_detail.append({"session": result.get("day") or result.get("session") or day, **row})
                for family, rows in (result.get("omissions") or {}).items():
                    for row in rows:
                        reason = row.get("reason")
                        omission_totals[f"{family}:{reason}"] += 1
                        # An error must be attributable: a bare count of eleven
                        # scan errors is not evidence of anything. Record the
                        # session, the branch and the exception text for each.
                        if reason == "scan_error":
                            scan_errors.append(
                                {
                                    "date": day,
                                    "family": family,
                                    "branch": row.get("branch"),
                                    "error": row.get("error"),
                                }
                            )
                for key, value in (result.get("opportunities") or {}).items():
                    opportunity_totals[key] += value
                for key, value in result["counts"].items():
                    for field, count in value.items():
                        totals[key][field] += count
                for family, payload in result["selection"].items():
                    entries_per_session[family].append(payload["n_entries"])
                    executed_per_session[family].append(payload.get("n_executed", 0))
                    round_trips_per_session[family].append(payload.get("n_round_trips", 0))
                    primary_play[family][payload["primary_play"]] += 1
                    for item in payload["entries"]:
                        if item["stop_points"]:
                            stop_points[family].append(item["stop_points"])
                        if item["r_multiple_at_target"]:
                            rr[family].append(item["r_multiple_at_target"])
                        outcomes[family][item["outcome"]] += 1
                read = result["reads"].get("JJ-TBR")
                if read:
                    classification[read["classification"]] += 1
                    range_bins[read["range_bin"]] += 1
                    open_locations[read["open_location"]] += 1
                gb_read = result["reads"].get("GB-FAIL")
                if gb_read:
                    day_model[gb_read["day_model"]] += 1
                for row in result["rows"]:
                    sink.write(json.dumps(row) + "\n")
                # one session line: the day reads and every variant's executed result,
                # for the fold evaluation (Phase 1.5 rebuilt plan)
                executed_rows = (result.get("variants") or {}).pop("__executed__", None)
                sink.write(json.dumps({"kind": "session", "date": result["date"], "reads": result["reads"], "variants": result.get("variants") or {}, "executed": executed_rows}, default=str) + "\n")
                for name, per_family in (result.get("variants") or {}).items():
                    for family, stats in per_family.items():
                        agg = variant_totals[(name, family)]
                        agg["sessions"] += 1
                        agg["net_points"] += stats["net_points"]
                        agg["trades"] += stats["n_executed"]
                        agg["round_trips"] += stats["n_round_trips"]
                        agg["wins"] += stats["wins"]
                        agg["losses"] += stats["losses"]
                        agg["open"] += stats["open"]
                if done % 50 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(dates),
                                      "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)

    wall = time.monotonic() - started
    summary = {
        "schema": "jj-gb-population-v1",
        "baseline_version": "B0.3-2026-09-17",
        "n_dates_requested": len(dates),
        "n_dates_complete": len(dates) - len(failures),
        "failures": failures,
        "workers": args.workers,
        "sessionstat_computed": bool(args.sessionstat),
        "wall_seconds": wall,
        "seconds_per_session_mean": (sum(per_date_seconds) / len(per_date_seconds)) if per_date_seconds else None,
        "peak_rss_bytes_worker": peak,
        "causality_violations": causality,
        "causality_detail": causality_detail,
        # Every omission a scan recorded, summed across the population: a branch
        # that never ran, a reference that could not be measured and a scan that
        # raised are all visible here rather than only inside the per-session row.
        "omission_reasons": dict(sorted(omission_totals.items())),
        "scan_errors": scan_errors,
        "branch_counts": {key: value for key, value in sorted(totals.items())},
        "opportunities": dict(opportunity_totals),
        "entries_per_session": {
            family: {
                "mean": (sum(values) / len(values)) if values else None,
                "distribution": dict(Counter(values)),
                "n_sessions": len(values),
            }
            for family, values in entries_per_session.items()
        },
        "executed_per_session": {
            family: {"mean": (sum(values) / len(values)) if values else None, "n_sessions": len(values)}
            for family, values in executed_per_session.items()
        },
        "round_trips_per_session": {
            family: {"mean": (sum(values) / len(values)) if values else None, "distribution": dict(Counter(values)), "n_sessions": len(values)}
            for family, values in round_trips_per_session.items()
        },
        "author_trades_per_day": {"JJ-TBR": "1-3 (JR dated posts)", "GB-FAIL": "1-2 (GB dated posts)"},
        "stop_points": {family: _quantiles(values) for family, values in stop_points.items()},
        "r_multiple_at_target": {family: _quantiles(values) for family, values in rr.items()},
        "selected_trade_outcomes": {family: dict(counter) for family, counter in outcomes.items()},
        "scanner_overrides": scanner_overrides,
        "variants": {
            f"{name}|{family}": {**agg, "net_points": round(agg["net_points"], 2), "net_points_per_session": round(agg["net_points"] / agg["sessions"], 3) if agg["sessions"] else None, "trades_per_session": round(agg["trades"] / agg["sessions"], 2) if agg["sessions"] else None, "win_rate": round(agg["wins"] / (agg["wins"] + agg["losses"]), 3) if (agg["wins"] + agg["losses"]) else None}
            for (name, family), agg in sorted(variant_totals.items())
        },
        "jumbo_classification": dict(classification),
        "jumbo_range_bins": dict(range_bins),
        "jumbo_open_locations": dict(open_locations),
        "greenbird_day_model": dict(day_model),
        "primary_play": {family: dict(counter) for family, counter in primary_play.items()},
    }
    (args.out / "POPULATION.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    (args.out / "POPULATION.md").write_text(render(summary))
    print(json.dumps({"event": "population_complete", "dates": len(dates), "wall_s": round(wall, 1),
                      "peak_rss_gb": round(peak / 2**30, 2), "causality_violations": causality}))
    return 0


def render_variants(summary) -> list[str]:
    rows = summary.get("variants") or {}
    if not rows:
        return []
    lines = ["", "## Executed-list results by selection variant (points a contract, no costs)", "", "| variant | family | sessions | net points / session | trades / session | win rate | round trips | open |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for key, agg in rows.items():
        name, family = key.split("|", 1)
        lines.append(f"| {name} | {family} | {agg['sessions']} | {agg['net_points_per_session']} | {agg['trades_per_session']} | {agg['win_rate']} | {agg['round_trips']} | {agg['open']} |")
    return lines


def render(summary) -> str:
    lines = [
        "# Population, source-faithful Jumbo and Green Bird (B0.3-2026-09-17)",
        "",
        f"- sessions: {summary['n_dates_complete']} of {summary['n_dates_requested']} (failures: {len(summary['failures'])})",
        f"- wall: {summary['wall_seconds']:.1f}s on {summary['workers']} workers; {summary['seconds_per_session_mean']:.2f}s per session per worker",
        f"- worker peak RSS: {summary['peak_rss_bytes_worker'] / 2**30:.2f} GB",
        f"- causality violations (decision_at < max stage at_ns): {summary['causality_violations']}",
        f"- scan errors (each attributable): {len(summary['scan_errors'])}"
        + (f" -- {summary['scan_errors'][0]['date']} {summary['scan_errors'][0]['branch']}: {str(summary['scan_errors'][0]['error'])[:90]}" if summary["scan_errors"] else ""),
        f"- omissions recorded: {sum(summary['omission_reasons'].values())} "
        f"({', '.join(f'{k}={v}' for k, v in list(summary['omission_reasons'].items())[:8]) or 'none'})",
        f"- SessionStat envelope computed: {summary['sessionstat_computed']}",
        "",
        "## Branch population",
        "",
        "An opportunity is one (side, reference, cycle) that passed; the entry modes are",
        "alternative fills of the same opportunity, not separate setups.",
        "",
        "| family | branch | episodes | pass | fail | unknown | pass/session | opportunities/session |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    n = max(1, summary["n_dates_complete"])
    for key, value in summary["branch_counts"].items():
        family, branch = key.split("|", 1)
        lines.append(
            f"| {family} | {branch} | {value['episodes']} | {value['pass']} | {value['fail']} | {value['unknown']} | {value['pass'] / n:.2f} | {summary['opportunities'].get(key, 0) / n:.2f} |"
        )
    lines += ["", "## Selected trade list (the author's frequency)", "",
              "| family | entries/session mean | distribution | outcomes |", "| --- | --- | --- | --- |"]
    for family, value in summary["entries_per_session"].items():
        lines.append(
            f"| {family} | {value['mean']:.2f} | {value['distribution']} | {summary['selected_trade_outcomes'].get(family)} |"
        )
    lines += ["", "## Risk and reward on the selected trades", "",
              "| family | stop points (min/p25/median/p75/p90/max) | R:R at target |", "| --- | --- | --- |"]
    for family in summary["stop_points"]:
        sp = summary["stop_points"][family]
        rr = summary["r_multiple_at_target"].get(family, {})
        lines.append(
            "| {f} | {a} / {b} / {c} / {d} / {e} / {g} | median {m} |".format(
                f=family, a=sp.get("min"), b=sp.get("p25"), c=sp.get("median"), d=sp.get("p75"),
                e=sp.get("p90"), g=sp.get("max"), m=rr.get("median"))
        )
    lines += ["", "## Day reads", "",
              f"- Jumbo classification: {summary['jumbo_classification']}",
              f"- Jumbo range bins: {summary['jumbo_range_bins']}",
              f"- Jumbo open locations: {summary['jumbo_open_locations']}",
              f"- Green Bird day model: {summary['greenbird_day_model']}",
              f"- primary play: {summary['primary_play']}",
              ""]
    lines += render_variants(summary)
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
