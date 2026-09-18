#!/usr/bin/env python3
"""Measure a traded-list policy on the dated tickets without rescanning.

A ticket replay spends almost all of its time scanning each session; the
selection that turns a session's episodes into the traded list takes
milliseconds. This tool scans each ticket session ONCE (episodes cached under
``--cache``, keyed by the adapter files' content so a scanner change rescans)
and then evaluates any number of policies, each a set of module constants, on
three things that are only evidence together (user rule 2026-09-18):

  * trades a ticket day on the TRADED (executed) list,
  * the author's tickets on that list (within ten points on the right bar,
    the replay's own matcher),
  * fake tickets on that list (``placebo_examples_jj_gb.py``: the same tickets
    moved in time on their own day and side, priced at the market).

    policy_lab.py --family GB --cache <dir> --out <file.json> \
        --policies '{"baseline": {}, "five-minute trigger": {"green_b02.TRADED_MODES": ["five_minute_close"]}}' \
        [--fake fake_40.json,fake_-40.json]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pickle
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADAPTERS = HERE.parents[0] / "src/trading_research/research/rule_discovery/source_adapters"


def _module(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def scanner_tag(family: str) -> str:
    """Content hash of the files a scan depends on: a changed scanner gets a new cache."""
    names = ("jumbo.py", "jumbo_context.py", "session_levels.py") if family == "JJ" else ("green_b02.py", "green_failure.py", "green_vwap_scalp.py", "session_levels.py")
    digest = hashlib.sha256()
    for name in names:
        digest.update((ADAPTERS / name).read_bytes())
    return digest.hexdigest()[:12]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=("JJ", "GB"), required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--policies", required=True, help="JSON: {name: {\"module.CONSTANT\": value}}")
    parser.add_argument("--fake", default="", help="comma-separated fake-ticket files")
    parser.add_argument("--show", default=None, help="print every ticket's traded list for this policy")
    args = parser.parse_args(argv)
    replay = _module("replay_jj_gb")
    from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
    from trading_research.research.rule_discovery.source_adapters import jumbo as jj
    from trading_research.research.rule_discovery.source_adapters import trade_selection as ts

    modules = {"green_b02": gb, "jumbo": jj, "trade_selection": ts}
    module = jj if args.family == "JJ" else gb
    policies = json.loads(args.policies)
    cache = args.cache / args.family / scanner_tag(args.family)
    cache.mkdir(parents=True, exist_ok=True)
    markets = replay.Markets()
    sets = {"real": json.loads(replay.EXAMPLES.read_text())["examples"]}
    for path in [p for p in args.fake.split(",") if p]:
        sets[Path(path).stem] = json.loads(Path(path).read_text())["examples"]

    def episodes_for(day: str):
        path = cache / f"{day}.pkl"
        if path.is_file():
            return pickle.loads(path.read_bytes())
        market = markets.get(day)
        if args.family == "JJ":
            document = jj.scan_b02(market, {"branch": "all"})
            body = {"episodes": document.get("episodes") or [], "read": document.get("day_read") or {}}
        else:
            episodes, read = [], {}
            for item in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
                doc = gb.scan_b02(market, {"family": item, "branch": "all"})
                episodes.extend(doc.get("episodes") or [])
                read = read or (doc.get("day_read") or {})
            body = {"episodes": episodes, "read": read}
        path.write_bytes(pickle.dumps(body))
        return body

    report: dict = {}
    for name, overrides in policies.items():
        saved = {}
        for key, value in overrides.items():
            mod, const = key.split(".", 1)
            if not hasattr(modules[mod], const):
                raise SystemExit(f"{key}: no such constant")
            saved[key] = getattr(modules[mod], const)
            setattr(modules[mod], const, tuple(value) if isinstance(value, list) and isinstance(saved[key], tuple) else value)
        try:
            body: dict = {}
            for label, examples in sets.items():
                hits = total = 0
                per_day: dict[str, int] = {}
                lines = []
                for example in examples:
                    if not str(example.get("id", "")).startswith(args.family) or not example.get("inside_tape"):
                        continue
                    for entry in module.proper_entries(example):
                        session = replay._session_date(entry)
                        if session is None or session.isoformat() not in markets.calendar:
                            continue
                        day = session.isoformat()
                        scanned = episodes_for(day)
                        market = markets.get(day)
                        selected = replay._selection_for_session(module, market, scanned["episodes"], scanned["read"])
                        match = module.match_entry(market, selected.get("executed_episodes") or [], entry)
                        ok = replay.strict_10(entry, match)
                        total += 1
                        hits += ok
                        per_day[day] = len(selected.get("executed_trades") or [])
                        if label == "real":
                            trades = " ".join(f'{t["at_et"]}{t["side"][0]}:{str(t["branch"])[:9]}:{str(t.get("mode"))[:7]}:{str(t["outcome"])[:1]}' for t in selected.get("executed_trades") or [])
                            lines.append(f'{"EXEC" if ok else "miss"} {example["id"]:22s} {str(entry.get("time_et")):14s} {str(entry.get("side")):5s} | {trades}')
                counts = list(per_day.values())
                body[label] = {"tickets": total, "on_traded_list": hits, "rate": round(hits / max(1, total), 3), "traded_a_day_median": statistics.median(counts) if counts else None, "traded_a_day_max": max(counts) if counts else None}
                if label == "real" and args.show == name:
                    print("\n".join(lines))
            fake_hits = sum(v["on_traded_list"] for k, v in body.items() if k != "real")
            fake_total = sum(v["tickets"] for k, v in body.items() if k != "real")
            body["fake_rate"] = None if not fake_total else round(fake_hits / fake_total, 3)
            report[name] = {"overrides": overrides, **body}
            real = body["real"]
            print(f'{name:34s} traded/day median {real["traded_a_day_median"]} max {real["traded_a_day_max"]} | tickets {real["on_traded_list"]}/{real["tickets"]} ({real["rate"]}) | fake {fake_hits}/{fake_total} ({body["fake_rate"]})', flush=True)
        finally:
            for key, value in saved.items():
                mod, const = key.split(".", 1)
                setattr(modules[mod], const, value)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
