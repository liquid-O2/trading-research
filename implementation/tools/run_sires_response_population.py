#!/usr/bin/env python3
"""Sires' entry at failed aggression over the whole tape, from the trades: one
row per fill of every failure (``source_adapters/sires_responses``): the
``reclaim`` (the trade that takes a big aggressive order's price back) and the
``arrival`` (the other side's first big order after it). Every feature is a
fact known at the row's ``decision_at``; outcomes carry the ``label_`` prefix.

Features, in his words:

  effort        how many big orders failed together, their contracts, the
                largest, how far they were paid before losing it, how long
                the failure took (Big Trades p.4: "Aggression is effort")
  location      where the failure sits in the day's range, whether the failed
                side's extreme IS the day's extreme ("sellers absorbed at the
                bottom"), the cash open, the overnight extremes, the prior
                session's high, low, close and value area (his "location")
  flow, state   signed aggressor volume and price travel into the decision,
                big orders of each side in the last minute, speed of tape
                against its ten-minute norm, CVD against its own session
                median (Big Trades p.12), the clock

Labels: MFE and MAE in points from the entry at 5, 15, 30 and 60 minutes, and
the favourable excursion reached before the stop (a tick beyond the failed
side's extreme) in units of that stop's distance. No exit is chosen here.

    run_sires_response_population.py --out <dir> [--workers 4] [--dates a,b] [--limit N]
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
SECOND = 1_000_000_000
BATCH = 40  # sessions a pool lives for (long-lived workers grow; max_tasks_per_child deadlocks here)


def scan_one(day: str) -> dict:
    import numpy as np

    from trading_research.research.method_pack import trade_tape as tt
    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters import sires_responses as sr
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market
    from trading_research.research.rule_discovery.source_adapters.session_levels import prior_sessions, prior_value_area

    install_write_guard()
    started = time.monotonic()
    market = load_source_market(day)
    start, end = int(market.start), int(market.end)
    tape = tt.trades_between(market.data_root, int(market.instrument_id), start, end)
    if tape is None:
        return {"date": day, "covered": False, "rows": [], "seconds": round(time.monotonic() - started, 1)}
    t, px, size, sign = tape
    open_ns, close_ns = int(market.at("09:30")), int(market.at("16:00"))
    events = sr.failed_aggression(t, px, size, sign, begin=start, end=close_ns)
    ot, osg, lots, _olo, _ohi = tt.aggressive_orders(t, px, size, sign)
    big = lots >= sr.MIN_LOTS
    big_t, big_sign = ot[big], osg[big]
    signed = np.cumsum(size * sign)
    k_open = int(np.searchsorted(t, open_ns))
    cash_open = float(px[k_open]) if k_open < len(px) else None
    overnight = px[:k_open]
    on_hi, on_lo = (float(overnight.max()), float(overnight.min())) if len(overnight) else (None, None)
    prior = value = None
    try:
        spans = prior_sessions(market, 1)
        if spans:
            prior = {k: (None if spans[0].get(k) is None else float(spans[0][k])) for k in ("high", "low", "close")}
        area = prior_value_area(market)
        if area:
            value = {k: (None if area.get(k) is None else float(area[k])) for k in ("vah", "val", "poc")}
    except Exception:
        pass
    running_hi = np.maximum.accumulate(px)
    running_lo = np.minimum.accumulate(px)
    rows = []
    for event in events:
        long = event["side"] == "long"
        s = 1 if long else -1
        fills = [("reclaim", event["decision_at"], event["entry"], None, event["stop"])]
        if event.get("arrival"):
            fills.append(("arrival", event["arrival"]["decision_at"], event["arrival"]["entry"], event["arrival"]["lots"], event["arrival"]["stop"]))
        for mode, at, entry, arrival_lots, stop in fills:
            k = int(np.searchsorted(t, at, side="right")) - 1
            if k < 0:
                continue
            risk = (entry - stop) * s
            if risk <= 0:
                continue
            day_hi, day_lo = float(running_hi[k]), float(running_lo[k])

            def back(seconds):
                return int(np.searchsorted(t, at - seconds * SECOND))

            k30, k120, k600 = back(30), back(120), back(600)
            b60 = (big_t >= at - 60 * SECOND) & (big_t < at)
            stride = max(1, (k + 1) // 2000)
            cvd_median = float(np.median(signed[: k + 1 : stride]))
            ref = event["failed_ref"]
            row = {
                "family": "SIRES",
                "branch": "failed_aggression",
                "mode": mode,
                "session": day,
                "decision_at": at,
                "side": event["side"],
                "entry": entry,
                "stop": stop,
                "segment": "cash" if at >= open_ns else "overnight",
                "minutes_from_open": round((at - open_ns) / MINUTE, 2),
                # effort
                "failed_orders": event["failed_orders"],
                "failed_contracts": event["failed_contracts"],
                "failed_largest": event["failed_largest"],
                "paid_points": event["paid_points"],
                "seconds_to_fail": event["seconds_to_fail"],
                "seconds_after_reclaim": round((at - event["decision_at"]) / 1e9, 1),
                "arrival_lots": arrival_lots,
                "risk_points": round(risk, 2),
                # location
                "failed_extreme_is_day_extreme": bool(abs(event["extreme"] - (day_lo if long else day_hi)) <= 2.0),
                "position_in_day_range": None if day_hi == day_lo else round((ref - day_lo) / (day_hi - day_lo), 3),
                "day_range_points": round(day_hi - day_lo, 2),
                "points_from_cash_open": None if cash_open is None or at < open_ns else round((ref - cash_open) * s, 2),
                "points_above_overnight_high": None if on_hi is None or at < open_ns else round(ref - on_hi, 2),
                "points_below_overnight_low": None if on_lo is None or at < open_ns else round(on_lo - ref, 2),
                "points_from_prior_high": None if not prior or prior["high"] is None else round(ref - prior["high"], 2),
                "points_from_prior_low": None if not prior or prior["low"] is None else round(ref - prior["low"], 2),
                "points_from_prior_close": None if not prior or prior["close"] is None else round(ref - prior["close"], 2),
                "points_from_prior_vah": None if not value or value["vah"] is None else round(ref - value["vah"], 2),
                "points_from_prior_val": None if not value or value["val"] is None else round(ref - value["val"], 2),
                "points_from_prior_poc": None if not value or value["poc"] is None else round(ref - value["poc"], 2),
                # flow and state, signed for the trade's side
                "delta_30s_with_side": int((signed[k] - signed[k30]) * s) if k30 < k else 0,
                "delta_120s_with_side": int((signed[k] - signed[k120]) * s) if k120 < k else 0,
                "travel_points_120s_with_side": round(float(px[k] - px[k120]) * s, 2) if k120 < k else 0.0,
                "big_orders_with_side_60s": int((big_sign[b60] == s).sum()),
                "big_orders_against_side_60s": int((big_sign[b60] == -s).sum()),
                "tape_speed_ratio": round(((k - k30) / 30.0) / max(1e-9, (k - k600) / 600.0), 3) if k600 < k30 < k else None,
                "cvd_vs_median_with_side": int((signed[k] - cvd_median) * s),
            }
            after = px[k + 1 :]
            after_t = t[k + 1 :]
            for minutes in (5, 15, 30, 60):
                j = int(np.searchsorted(after_t, min(at + minutes * MINUTE, end)))
                seg = after[:j]
                if len(seg) == 0:
                    row[f"label_mfe_{minutes}"] = row[f"label_mae_{minutes}"] = 0.0
                    continue
                row[f"label_mfe_{minutes}"] = round(float((seg.max() - entry) if long else (entry - seg.min())), 2)
                row[f"label_mae_{minutes}"] = round(float((entry - seg.min()) if long else (seg.max() - entry)), 2)
            stopped = np.flatnonzero(after <= stop) if long else np.flatnonzero(after >= stop)
            upto = after[: int(stopped[0])] if stopped.size else after
            best = 0.0 if len(upto) == 0 else float((upto.max() - entry) if long else (entry - upto.min()))
            row["label_stopped"] = bool(stopped.size)
            row["label_minutes_to_stop"] = round((int(after_t[int(stopped[0])]) - at) / MINUTE, 2) if stopped.size else None
            row["label_mfe_before_stop_r"] = round(max(0.0, best) / risk, 3)
            rows.append(row)
    return {"date": day, "covered": True, "rows": rows, "n_events": len(events), "seconds": round(time.monotonic() - started, 1), "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}


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
    done = 0
    peak = 0
    with (args.out / "rows.jsonl").open("w") as sink:
        for offset in range(0, len(dates), BATCH * max(1, args.workers)):
            batch = dates[offset : offset + BATCH * max(1, args.workers)]
            with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
                futures = {pool.submit(scan_one, day): day for day in batch}
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
                    stats["events"] += result["n_events"]
                    peak = max(peak, int(result.get("peak_rss_bytes") or 0))
                    for row in result["rows"]:
                        sink.write(json.dumps(row) + "\n")
                        stats["rows"] += 1
                        stats[f"rows_{row['mode']}"] += 1
                    if done % 25 == 0:
                        print(json.dumps({"event": "progress", "done": done, "of": len(dates), "rows": stats["rows"], "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    n = max(1, stats["sessions"])
    summary = {"schema": "sires-response-population-v1", "n_dates_requested": len(dates), "n_dates_complete": done, "sessions_covered": stats["sessions"], "sessions_not_covered": len(uncovered), "failures": failures, "events": stats["events"], "events_per_session": round(stats["events"] / n, 1), "rows": stats["rows"], "rows_reclaim": stats["rows_reclaim"], "rows_arrival": stats["rows_arrival"], "peak_worker_rss_gb": round(peak / 2**30, 2), "wall_seconds": round(time.monotonic() - started, 1), "workers": args.workers}
    (args.out / "POPULATION.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"event": "population_complete", **{k: v for k, v in summary.items() if k != "failures"}, "n_failures": len(failures)}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
