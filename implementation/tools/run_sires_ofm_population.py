#!/usr/bin/env python3
"""Sires' OFM events over the whole tape, from the trades: one row per fill of
every completed sequence (``source_adapters/sires_ofm.scan_session``), with
the features his own research names as what selects a trade -- construction
(how much size built the catalyst), memory (has the area printed aggression
before, has it been tested), location (where it sits in the session and
against the prior day) -- the sequence's own facts (how far and how fast the
squeeze ran, how fast it failed, the aggressor balance of the retest bar), and
exit-agnostic outcome labels (MFE and MAE from the fill, in points, over the
next 5, 15, 30 and 60 minutes of trades). The Refill Effect: "Aggression
builds the level. It is the level's history that predicts the next touch";
"selection is what flips the sign".

    run_sires_ofm_population.py --out <dir> [--workers 4] [--dates a,b] [--limit N]

Every feature uses the tape up to the fill's own time; labels carry the
``label_`` prefix. Sessions before the owned trades files begin (2021-08-30)
are reported as not covered, not as empty.
"""
from __future__ import annotations

import argparse
import json
import resource
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

MINUTE = 60 * 1_000_000_000
HORIZONS = (5, 15, 30, 60)


def scan_one(day: str) -> dict:
    import numpy as np

    from trading_research.research.method_pack import trade_tape as tt
    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters import sires_ofm as ofm
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    install_write_guard()
    started = time.monotonic()
    market = load_source_market(day)
    start, end = int(market.start), int(market.end)
    result = ofm.scan_session(market)
    if result.get("reason"):
        return {"date": day, "covered": False, "reason": result["reason"], "rows": [], "n_sequences": 0, "seconds": round(time.monotonic() - started, 1)}
    tape = tt.trades_between(market.data_root, int(market.instrument_id), start, end)
    t, px = tape[0], tape[1]
    open_ns, close_ns = int(market.at("09:30")), int(market.at("16:00"))
    # session references known at any moment of the cash session
    overnight = px[(t < open_ns)]
    on_hi, on_lo = (float(overnight.max()), float(overnight.min())) if len(overnight) else (None, None)
    # the prior full session's high, low and close (the D-1 levels the authors draw), from the shared helper
    prior = None
    try:
        from trading_research.research.rule_discovery.source_adapters.session_levels import prior_sessions

        spans = prior_sessions(market, 1)
        if spans:
            prior = {"high": float(spans[0]["high"]), "low": float(spans[0]["low"]), "close": None if spans[0].get("close") is None else float(spans[0]["close"])}
    except Exception:
        prior = None
    sequences = result["sequences"]
    rows = []
    for n, s in enumerate(sequences):
        lo, hi = float(s["box_lo"]), float(s["box_hi"])
        earlier = sequences[:n]
        for fill in s["fills"]:
            at = int(fill["at"])
            entry, stop = float(fill["entry"]), float(fill["stop"])
            sign = 1 if s["side"] == "long" else -1
            k = int(np.searchsorted(t, at, side="right"))
            spot_open = float(px[np.searchsorted(t, open_ns)]) if open_ns < at and np.searchsorted(t, open_ns) < len(px) else None
            upto = px[:k]
            day_hi, day_lo = (float(upto.max()), float(upto.min())) if k else (None, None)
            row = {
                "family": "SIRES",
                "branch": "ofm",
                "session": day,
                "decision_at": at,
                "side": s["side"],
                "mode": fill["mode"],
                "catalyst_kind": s["catalyst_kind"],
                "entry": entry,
                "stop": stop,
                "stop_points": round(abs(entry - stop), 2),
                "cash_session": bool(open_ns <= at < close_ns),
                "minutes_from_open": round((at - open_ns) / MINUTE, 2),
                # construction
                "catalyst_orders": int(s["n_orders"]),
                "catalyst_lots": int(s["contracts"]),
                "catalyst_width": round(hi - lo, 2),
                # the sequence's own facts
                "squeeze_points": round(abs(float(s["squeeze_extreme"]) - (hi if s["side"] == "short" else lo)), 2),
                "seconds_catalyst_to_release": round((int(s["release_at"]) - int(s["catalyst_at"])) / 1e9, 1),
                "seconds_release_to_failure": round((int(s["failure_at"]) - int(s["release_at"])) / 1e9, 1),
                "seconds_failure_to_retest": round((int(s["retest_at"]) - int(s["failure_at"])) / 1e9, 1),
                "retest_buy_share": None if not (s["retest_bar"]["buy_volume"] + s["retest_bar"]["sell_volume"]) else round(s["retest_bar"]["buy_volume"] / (s["retest_bar"]["buy_volume"] + s["retest_bar"]["sell_volume"]), 3),
                "retest_volume": int(s["retest_bar"]["V"]),
                # memory: earlier completed sequences at the same area, and on the same side
                "prior_sequences_same_area": sum(1 for e in earlier if float(e["box_lo"]) <= hi + 6 and float(e["box_hi"]) >= lo - 6),
                "prior_sequences_same_side_today": sum(1 for e in earlier if e["side"] == s["side"]),
                # location
                "position_in_day_range": None if day_hi is None or day_hi == day_lo else round((entry - day_lo) / (day_hi - day_lo), 3),
                "points_from_cash_open": None if spot_open is None else round((entry - spot_open) * sign, 2),
                "points_beyond_overnight_high": None if on_hi is None else round(entry - on_hi, 2),
                "points_beyond_overnight_low": None if on_lo is None else round(on_lo - entry, 2),
                "points_from_prior_high": None if prior is None else round(entry - prior["high"], 2),
                "points_from_prior_low": None if prior is None else round(entry - prior["low"], 2),
                "points_from_prior_close": None if prior is None or prior["close"] is None else round(entry - prior["close"], 2),
            }
            for h in HORIZONS:
                j = int(np.searchsorted(t, min(at + h * MINUTE, end), side="left"))
                if j <= k:
                    row[f"label_mfe_{h}"] = row[f"label_mae_{h}"] = None
                    continue
                seg = px[k:j]
                row[f"label_mfe_{h}"] = round((float(seg.max()) - entry) if sign == 1 else (entry - float(seg.min())), 2)
                row[f"label_mae_{h}"] = round((entry - float(seg.min())) if sign == 1 else (float(seg.max()) - entry), 2)
            rows.append(row)
    return {"date": day, "covered": True, "rows": rows, "n_sequences": len(sequences), "n_bars": result.get("n_bars"), "seconds": round(time.monotonic() - started, 1), "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dates", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    if args.dates:
        dates = [d.strip() for d in args.dates.split(",") if d.strip()]
    else:
        from trading_research.research.method_pack import historical_runner as hr
        from trading_research.research.rule_discovery.baseline import PHASE1_RUN
        from trading_research.research.rule_discovery.run_baseline_repair import evaluation_dates

        registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
        dates = [str(d) for d in evaluation_dates(registry)]
    if args.limit:
        dates = dates[: args.limit]
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    failures, uncovered = [], []
    stats = Counter()
    peak = 0
    done = 0
    with (args.out / "rows.jsonl").open("w") as sink:
        with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(scan_one, day): day for day in dates}
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    failures.append({"date": day, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                done += 1
                if not result["covered"]:
                    uncovered.append(day)
                    continue
                stats["sessions"] += 1
                stats["sequences"] += result["n_sequences"]
                stats["cash_sequences"] += len({(r["decision_at"], r["side"]) for r in result["rows"] if r["cash_session"] and r["mode"] == "ofm_passive"} | {(r["decision_at"], r["side"]) for r in result["rows"] if r["cash_session"]})
                peak = max(peak, int(result.get("peak_rss_bytes") or 0))
                for row in result["rows"]:
                    sink.write(json.dumps(row) + "\n")
                    stats["rows"] += 1
                sink.write(json.dumps({"kind": "session", "date": day, "n_sequences": result["n_sequences"], "n_rows": len(result["rows"]), "seconds": result["seconds"]}) + "\n")
                if done % 25 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(dates), "rows": stats["rows"], "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    n = max(1, stats["sessions"])
    summary = {"schema": "sires-ofm-population-v1", "n_dates_requested": len(dates), "n_dates_complete": done, "sessions_covered": stats["sessions"], "sessions_not_covered": len(uncovered), "failures": failures, "rows": stats["rows"], "sequences_per_session": round(stats["sequences"] / n, 2), "wall_seconds": round(time.monotonic() - started, 1), "peak_rss_bytes_worker": peak, "workers": args.workers}
    (args.out / "POPULATION.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"event": "population_complete", **{k: v for k, v in summary.items() if k != "failures"}, "n_failures": len(failures)}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
