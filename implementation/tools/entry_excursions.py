#!/usr/bin/env python3
"""Exit-agnostic entry quality: for every entry of a list (executed trades or
candidates, any family), the maximum favourable excursion (MFE) and maximum
adverse excursion (MAE) over fixed horizons after the decision, from the same
one-minute bars the scanners read. No stop, no target, no management: an entry
is judged by where price went after it, so an entry-side upgrade cannot be
confused with a change of the stop or objective convention (2026-09-18: three
"entry" reads were stop reads under the net-points metric).

    entry_excursions.py --entries rows.jsonl [--entries more.jsonl] --out <dir>
        [--workers 4] [--dates a,b] [--limit N]

Entry sources understood (one JSON object a line):
  * ``{"kind": "entry", "family", "date", "side", "entry", "decision_at", ...}``
    (the per-entry records of run_exits_population.py);
  * a population session line carrying ``"executed"`` and/or ``"candidates"``
    lists (run_jj_gb_population.py, run_sires_population.py,
    run_saint_population.py); the list an entry came from is kept as ``list``.

Causality: only bars that START at or after ``decision_at`` count, so the
decision bar's own range (part of which precedes the decision) never enters.
Excursions are in points and in basis points of the entry price (NQ tripled
over the tape; points are not comparable across years).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
MINUTE = 60 * 1_000_000_000
HORIZONS = (15, 30, 60, 120)  # minutes; "eos" (to the end of the entry's session clock) is added


def _module(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_entries(paths: list[Path], dates: set[str] | None) -> dict[str, list[dict]]:
    per_day: dict[str, list[dict]] = defaultdict(list)

    def add(day, family, side, entry, at, source, extra):
        if day is None or entry is None or at is None or side not in ("long", "short"):
            return
        if dates is not None and day not in dates:
            return
        per_day[day].append({"date": day, "family": family, "side": side, "entry": float(entry), "decision_at": int(at), "list": source, **extra})

    for path in paths:
        with path.open() as handle:
            for line in handle:
                if '"kind": "entry"' in line:
                    r = json.loads(line)
                    add(r.get("date"), r.get("family"), r.get("side"), r.get("entry"), r.get("decision_at"), "executed", {"branch": r.get("branch"), "mode": r.get("mode"), "id": r.get("entry_id")})
                elif '"kind": "session"' in line and ('"executed"' in line or '"candidates"' in line):
                    r = json.loads(line)
                    for item in r.get("executed") or []:
                        add(r.get("date"), item.get("family"), item.get("side"), item.get("entry"), item.get("decision_at"), "executed", {"branch": item.get("branch"), "mode": item.get("mode"), "id": item.get("candidate_id")})
                    for item in r.get("candidates") or []:
                        geometry = item.get("geometry") or {}
                        family = item.get("family") or next(iter((r.get("variants") or {}).get("B0.3") or {}), None)
                        add(r.get("date"), family, item.get("side"), geometry.get("entry"), item.get("decision_at"), "candidate", {"branch": item.get("branch"), "mode": (item.get("values") or {}).get("confirmation_mode"), "id": item.get("candidate_id")})
    return per_day


def excursions_one(day: str, entries: list[dict]) -> dict:
    import numpy as np

    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    install_write_guard()
    rs = _module("replay_sires")
    started = time.monotonic()
    market = load_source_market(day)
    start_ns, end_ns = int(market.start), int(market.end)
    bars = rs.bars_between(market, start_ns, end_ns)
    starts = np.array([int(b["start"]) for b in bars], dtype=np.int64)
    highs = np.array([float(b["H"]) for b in bars], dtype=float)
    lows = np.array([float(b["L"]) for b in bars], dtype=float)
    rth_end = int(market.at("16:00"))
    out = []
    for e in entries:
        at, px, sign = e["decision_at"], e["entry"], (1 if e["side"] == "long" else -1)
        i = int(np.searchsorted(starts, at, side="left"))
        # the entry's own session clock: a cash-session entry is followed to 16:00, any other to the account day's end
        eos = rth_end if at < rth_end else end_ns
        row = dict(e)
        for label, until in [(str(h), min(at + h * MINUTE, end_ns)) for h in HORIZONS] + [("eos", eos)]:
            j = int(np.searchsorted(starts, until, side="left"))
            if j <= i:
                row[f"mfe_{label}"] = row[f"mae_{label}"] = None
                continue
            hi, lo = float(highs[i:j].max()), float(lows[i:j].min())
            mfe = (hi - px) if sign == 1 else (px - lo)
            mae = (px - lo) if sign == 1 else (hi - px)
            row[f"mfe_{label}"] = round(mfe, 2)
            row[f"mae_{label}"] = round(mae, 2)
            row[f"bars_{label}"] = j - i
        out.append(row)
    return {"date": day, "rows": out, "seconds": round(time.monotonic() - started, 1)}


def summarize(rows_path: Path) -> list[str]:
    import statistics

    groups: dict[tuple, list[dict]] = defaultdict(list)
    with rows_path.open() as handle:
        for line in handle:
            r = json.loads(line)
            groups[(r["family"], r["list"], "ALL")].append(r)
            groups[(r["family"], r["list"], str(r.get("branch")))].append(r)
    lines = ["# Entry excursions (exit-agnostic)", "", "MFE and MAE in basis points of the entry price; `edge` = mean MFE / mean MAE; `favourable first` = share of entries whose MFE exceeds their MAE over the horizon.", ""]
    for horizon in ("30", "60", "eos"):
        lines += [f"## Horizon {horizon}{' minutes' if horizon != 'eos' else ' (to the end of the session clock)'}", "", "| family | list | branch | entries | mean MFE bps | mean MAE bps | edge | median MFE | median MAE | favourable first |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for (family, source, branch), rows in sorted(groups.items(), key=lambda kv: (kv[0][0] or "", kv[0][1], kv[0][2] != "ALL", -len(kv[1]))):
            pairs = [(r[f"mfe_{horizon}"] / r["entry"] * 1e4, r[f"mae_{horizon}"] / r["entry"] * 1e4) for r in rows if r.get(f"mfe_{horizon}") is not None]
            if len(pairs) < 30:
                continue
            mfe, mae = [p[0] for p in pairs], [p[1] for p in pairs]
            lines.append(f"| {family} | {source} | {branch} | {len(pairs)} | {statistics.mean(mfe):.1f} | {statistics.mean(mae):.1f} | {statistics.mean(mfe) / max(1e-9, statistics.mean(mae)):.3f} | {statistics.median(mfe):.1f} | {statistics.median(mae):.1f} | {sum(1 for a, b in pairs if a > b) / len(pairs):.3f} |")
        lines.append("")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entries", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dates", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    dates = None if not args.dates else set(args.dates.split(","))
    per_day = read_entries(args.entries, dates)
    days = sorted(per_day)
    if args.limit:
        days = days[: args.limit]
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    failures = []
    n_rows = done = 0
    with (args.out / "rows.jsonl").open("w") as sink:
        with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(excursions_one, day, per_day[day]): day for day in days}
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    failures.append({"date": day, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                done += 1
                for row in result["rows"]:
                    sink.write(json.dumps(row) + "\n")
                    n_rows += 1
                if done % 50 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(days), "rows": n_rows, "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    (args.out / "EXCURSIONS.md").write_text("\n".join(summarize(args.out / "rows.jsonl")) + "\n")
    summary = {"schema": "entry-excursions-v1", "sessions": done, "sessions_requested": len(days), "entries_in": sum(len(per_day[d]) for d in days), "rows": n_rows, "failures": failures, "wall_seconds": round(time.monotonic() - started, 1)}
    (args.out / "EXCURSIONS.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"event": "excursions_complete", **{k: v for k, v in summary.items() if k != "failures"}, "n_failures": len(failures)}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
