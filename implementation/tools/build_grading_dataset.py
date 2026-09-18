#!/usr/bin/env python3
"""The grading study's dataset: one row per admitted opportunity on every dated
Jumbo and Green Bird session, with the features the authors say they grade on
and the label (the opportunity that holds the author's ticket).

Positives: the author's proper entries (records). Negatives: every other
opportunity in the uncapped candidate list of that session. Features are
observations available at the decision (nothing after it):

* family, branch, play, side, segment, minutes from the cash open;
* the line: kind, cycle index at that line, sweep depth in points and in
  units of the box width (Jumbo), the line's distance from the day's open;
* confluence: PDH/PDL, PWH/PWL, TDO, Asia and London extremes, the prior
  value area edges, the 6-9 edges and projections within 5 points of the
  line (count and names);
* the day read: Jumbo classification, aligned, big range, open inside value;
  Green Bird day model, bias, overnight events;
* reward available: points to the first objective and to the far objective,
  stop points, R:R at the far objective.

Output: rows.jsonl and a CSV for the fitting script. No fitting here.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

from trading_research.research.rule_discovery.source_adapters import green_b02 as gb  # noqa: E402
from trading_research.research.rule_discovery.source_adapters import jumbo as jj  # noqa: E402
from trading_research.research.rule_discovery.source_adapters.common import load_source_market  # noqa: E402
from trading_research.research.rule_discovery.source_adapters.trade_selection import _episode_key, branch_alternatives  # noqa: E402

ET = ZoneInfo("America/New_York")
EXAMPLES = WORKTREE / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"
NS = 1_000_000_000
COINCIDE = Decimal("5")


def _f(v):
    try:
        return None if v is None else float(v)
    except Exception:
        return None


def minutes_from_open(market, ns: int) -> float:
    return round((int(ns) - int(market.at("09:30"))) / (60 * NS), 1)


def session_day(example, action) -> str:
    day = example["date"]
    hh = int(str(action["time_et"])[:2])
    if hh >= 18:
        d = date.fromisoformat(day) + timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        return d.isoformat()
    return day


def gb_context_levels(market) -> list[tuple[str, Decimal]]:
    refs, _ = gb.session_references(market)
    out = []
    for ref in refs:
        if ref.get("running") or str(ref["kind"]).startswith("hour_box"):
            continue
        for edge in ("low", "high"):
            if ref.get(edge) is not None:
                out.append((f"{ref['kind']}_{edge}", Decimal(str(ref[edge]))))
    tdo = gb._tdo(market)
    if tdo is not None:
        out.append(("tdo", Decimal(str(tdo))))
    return out


def jj_context_levels(market) -> list[tuple[str, Decimal]]:
    context = jj.session_context(market)
    out = []
    for row in context.get("levels") or []:
        if row.get("price") is not None:
            out.append((str(row.get("kind")), Decimal(str(row["price"]))))
    box = context.get("box") or {}
    for k in ("low", "high", "eq", "q25", "q75"):
        if box.get(k) is not None:
            out.append((f"box_{k}", Decimal(str(box[k]))))
    for name, px in (box.get("ladder") or {}).items():
        if px is not None:
            out.append((f"proj_{name}", Decimal(str(px))))
    return out


def confluence(level: Decimal | None, levels: list[tuple[str, Decimal]], own_kind: str) -> tuple[int, list[str]]:
    if level is None:
        return 0, []
    names = sorted({name for name, px in levels if abs(px - level) <= COINCIDE and not name.startswith(own_kind)})
    return len(names), names


def rows_for(family: str, example: dict, entries: list[dict], market, episodes: list[dict], selection: dict, read: dict) -> list[dict]:
    module = jj if family == "JJ" else gb
    levels = jj_context_levels(market) if family == "JJ" else gb_context_levels(market)
    # the opportunities in the uncapped candidate list, keyed
    by_id = {ep.get("candidate_id"): ep for ep in episodes}
    taken = selection.get("entries") or []
    keys = {}
    for row in taken:
        ep = by_id.get(row.get("candidate_id"))
        if ep is not None:
            keys[_episode_key(ep)] = row
    # which keys hold the author's tickets
    positives: dict[tuple, dict] = {}
    for entry in entries:
        match = module.match_entry(market, [ep for ep in episodes if _episode_key(ep) in keys], entry)
        if not match.get("detected_strict_10"):
            continue
        best = next((ep for ep in episodes if ep.get("candidate_id") is not None and ep.get("candidate_id") == (match.get("our_candidate_id") or match.get("candidate_id"))), None)
        if best is None:
            # identify the matched fill by branch, mode and entry price
            want_entry = _f(match.get("our_entry"))
            for ep in episodes:
                if _episode_key(ep) not in keys:
                    continue
                if ep.get("branch") != match.get("our_branch") or (ep.get("values") or {}).get("confirmation_mode") != match.get("our_mode"):
                    continue
                got = _f((ep.get("geometry") or {}).get("entry"))
                if got is not None and want_entry is not None and abs(got - want_entry) < 0.01:
                    best = ep
                    break
        if best is not None:
            positives[_episode_key(best)] = entry
    out = []
    for key, row in keys.items():
        ep = by_id.get(row.get("candidate_id")) or {}
        values = ep.get("values") or {}
        geometry = ep.get("geometry") or {}
        level = None
        try:
            level = Decimal(str(values.get("reference_px"))) if values.get("reference_px") is not None else None
        except Exception:
            level = None
        n_conf, names = confluence(level, levels, str(values.get("reference_kind") or ""))
        entry_px = _f(geometry.get("entry")); stop = _f(geometry.get("stop")); target = _f(geometry.get("target")); first = _f(values.get("first_objective") or geometry.get("first_objective"))
        box_width = None
        if family == "JJ":
            box = (jj.session_context(market).get("box") or {})
            box_width = _f(box.get("width"))
        depth = _f(values.get("sweep_depth") or values.get("depth_points"))
        out.append(
            {
                "family": family,
                "example_id": example["id"],
                "session": market.day if hasattr(market, "day") else None,
                "label": 1 if key in positives else 0,
                "decision_at": int(row.get("decision_at") or 0),
                "reference_px": _f(level),
                "entry_px": entry_px,
                "branch": ep.get("branch"),
                "play": module.PLAY_OF_BRANCH.get(ep.get("branch")),
                "side": ep.get("side"),
                "mode": values.get("confirmation_mode"),
                "minutes_from_open": minutes_from_open(market, int(row.get("decision_at") or 0)),
                "reference_kind": values.get("reference_kind"),
                "cycle": values.get("cycle"),
                "sweep_depth_points": depth,
                "sweep_depth_in_widths": None if depth is None or not box_width else round(depth / box_width, 3),
                "depth_class": values.get("depth_class"),
                "coincident_levels_n": n_conf,
                "coincident_levels": ";".join(names),
                "read_classification": read.get("classification"),
                "read_aligned": read.get("aligned"),
                "read_big_range": read.get("big_range"),
                "read_open_inside_value": read.get("open_inside_value"),
                "read_day_model": read.get("day_model"),
                "read_bias": read.get("bias"),
                "side_with_bias": None if not read.get("bias") else (ep.get("side") == read.get("bias")),
                # Jumbo's outside reads (TBR pp.22-24 and p.12); absent for Green Bird, whose read carries neither
                "read_news_tier": (read.get("news_week") or {}).get("tier"),
                "read_news_release_today": ";".join((read.get("news_week") or {}).get("release_today") or []) or None,
                "read_sister_divergence_on_side": None if not (read.get("sister_index") or {}).get("available") else bool(read["sister_index"]["divergence_at_high" if ep.get("side") == "short" else "divergence_at_low"]),
                "read_nq_minus_es_overnight_pct_with_side": None if not (read.get("sister_index") or {}).get("available") else round(float(read["sister_index"]["nq_minus_es_overnight_pct"]) * (1 if ep.get("side") == "long" else -1), 4),
                "stop_points": None if entry_px is None or stop is None else round(abs(entry_px - stop), 2),
                "first_objective_points": None if entry_px is None or first is None else round(abs(first - entry_px), 2),
                "far_objective_points": None if entry_px is None or target is None else round(abs(target - entry_px), 2),
                "rr_far": None if entry_px is None or stop is None or target is None or entry_px == stop else round(abs(target - entry_px) / abs(entry_px - stop), 2),
                "outcome": row.get("outcome"),
            }
        )
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", default=None)
    args = parser.parse_args(argv)
    jj.NY_ROUND_TRIPS = 99; jj.LONDON_ROUND_TRIPS = 99; gb.ROUND_TRIPS_PER_SEGMENT = 99  # uncapped candidate lists
    examples = json.loads(EXAMPLES.read_text())["examples"]
    wanted = set(args.only.split(",")) if args.only else None
    rows = []
    for ex in examples:
        if not ex.get("inside_tape") or not ex["id"].startswith(("JJ", "GB")):
            continue
        if wanted and ex["id"] not in wanted:
            continue
        family = ex["id"][:2]
        module = jj if family == "JJ" else gb
        entries = module.proper_entries(ex)
        if not entries:
            continue
        day = session_day(ex, entries[0]) if family == "GB" else ex["date"]
        market = load_source_market(day)
        if family == "JJ":
            doc = jj.scan_b02(market, {"branch": "all"}); episodes = [e for e in doc["episodes"] if e["research_verdict"] == "pass"]
            read = doc.get("day_read") or {}
            selection = jj.selection_for(market, episodes, primary_play=read.get("primary_play"))
        else:
            episodes = []
            for item in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
                episodes.extend(e for e in gb.scan_b02(market, {"family": item, "branch": "all"})["episodes"] if e["research_verdict"] == "pass")
            read = gb.session_read(market)
            selection = gb.selection_for(market, episodes)
        day_rows = rows_for(family, ex, entries, market, episodes, selection, read)
        rows.extend(day_rows)
        print(json.dumps({"id": ex["id"], "candidates": len(day_rows), "positives": sum(r["label"] for r in day_rows), "tickets": len(entries)}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "rows.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")
    if rows:
        with (args.out / "rows.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(json.dumps({"event": "dataset_complete", "rows": len(rows), "positives": sum(r["label"] for r in rows), "days": len({r["example_id"] for r in rows})}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
