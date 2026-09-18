#!/usr/bin/env python3
"""The Refill Effect's zone touches over the whole tape, from the trades: one
row per touch (``source_adapters/sires_zones``) with the paper's four feature
families, every one a fact known before the touch resolves:

  memory        which touch of this zone it is, how its earlier touches ended,
                how old the zone is, how long since it was last touched
  construction  how many big orders and contracts built it, its largest order,
                its width, whether one side built it, and whether that side is
                the one the touch fades (sellers absorbed under a support touch)
  location      where the edge sits in the day's range, against the cash open,
                the overnight extremes, the prior session's high, low and close
                and the prior session's value area
  flow, state   signed aggressor volume and price travel into the touch over
                the last 30 and 120 seconds, big orders into the level, clock

Labels (``label_`` prefix): held or broke (eight points either way from the
touched edge, within thirty minutes), the deepest dip past the edge, MFE and
MAE from the edge at 5, 15 and 30 minutes, and the PAPER'S OWN deployed trade
as published (limit twelve ticks inside the level, thirty-two-tick stop,
ninety-six-tick target, cancelled after thirty minutes) so the reconstruction
can be read against its reference numbers (fading every touch: -0.285R).

    run_sires_zone_population.py --out <dir> [--workers 4] [--dates a,b] [--limit N]

Zones: his thirty-lot prints chained by price (the box rule), a zone total of
at least ZONE_MIN_CONTRACTS, built since the session opened at 18:00; touches
are counted in the cash session. CALIBRATED on six sessions of the paper's
period to its ~175 touches a session (ours ~200).
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
ZONE_MIN_LOTS = 30
ZONE_MIN_CONTRACTS = 150
LEAVE_POINTS = 8.0
PAPER_ENTRY_INSIDE, PAPER_STOP, PAPER_TARGET, PAPER_CANCEL_MIN = 3.0, 8.0, 24.0, 30  # 12, 32 and 96 ticks; 30 minutes


def scan_one(day: str) -> dict:
    import numpy as np

    from trading_research.research.method_pack import trade_tape as tt
    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters import sires_ofm as ofm
    from trading_research.research.rule_discovery.source_adapters import sires_zones as sz
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market
    from trading_research.research.rule_discovery.source_adapters.session_levels import prior_sessions, prior_value_area

    install_write_guard()
    started = time.monotonic()
    market = load_source_market(day)
    start, end = int(market.start), int(market.end)
    tape = tt.trades_between(market.data_root, int(market.instrument_id), start, end)
    if tape is None:
        return {"date": day, "covered": False, "rows": [], "n_zones": 0, "seconds": round(time.monotonic() - started, 1)}
    t, px, size, sign = tape
    open_ns, close_ns = int(market.at("09:30")), int(market.at("16:00"))
    ot, osg, lots, olo, ohi = tt.aggressive_orders(t, px, size, sign)
    big = lots >= ZONE_MIN_LOTS
    zones = [z for z in ofm.cluster_boxes(ot[big], osg[big], lots[big], olo[big], ohi[big]) if z["known_at"] < close_ns and z["contracts"] >= ZONE_MIN_CONTRACTS]
    touches = sz.zone_touches(t, px, zones, begin=open_ns, end=close_ns, leave=LEAVE_POINTS)
    signed = np.cumsum(size * sign)
    big_t, big_sign = ot[big], osg[big]
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
    history: dict[int, list[str]] = {}
    last_touch: dict[int, int] = {}
    rows = []
    for touch in touches:
        z = zones[touch["zone"]]
        at, k = touch["at"], touch["trade_index"]
        long = touch["side"] == "long"
        s = 1 if long else -1
        edge = touch["edge"]
        lo, hi = float(z["lo"]), float(z["hi"])
        past = history.setdefault(touch["zone"], [])
        day_hi, day_lo = float(px[: k + 1].max()), float(px[: k + 1].min())

        def back(seconds):
            return int(np.searchsorted(t, at - seconds * SECOND))

        k30, k120 = back(30), back(120)
        b60 = (big_t >= at - 60 * SECOND) & (big_t < at)
        row = {
            "family": "SIRES",
            "branch": "zone_touch",
            "session": day,
            "decision_at": at,
            "side": touch["side"],
            "edge": edge,
            "minutes_from_open": round((at - open_ns) / MINUTE, 2),
            # memory
            "touch_number": len(past) + 1,
            "prior_holds": past.count("held"),
            "prior_breaks": past.count("broke"),
            "zone_age_minutes": round((at - int(z["known_at"])) / MINUTE, 1),
            "minutes_since_last_touch": None if touch["zone"] not in last_touch else round((at - last_touch[touch["zone"]]) / MINUTE, 1),
            "zone_built_overnight": bool(int(z["known_at"]) < open_ns),
            # construction
            "zone_orders": int(z["n_orders"]),
            "zone_contracts": int(z["contracts"]),
            "zone_largest": int(z["largest"]),
            "zone_width": round(hi - lo, 2),
            "zone_one_sided": z["sides"] in ("A", "B"),
            # the defended side: sellers absorbed (aggressor A) under a support touch, buyers (B) over a resistance touch
            "zone_aggressor_absorbed": bool((z["aggressor"] == "A") == long),
            # location
            "position_in_day_range": None if day_hi == day_lo else round((edge - day_lo) / (day_hi - day_lo), 3),
            "points_from_cash_open": None if cash_open is None else round((edge - cash_open) * s, 2),
            "points_above_overnight_high": None if on_hi is None else round(edge - on_hi, 2),
            "points_below_overnight_low": None if on_lo is None else round(on_lo - edge, 2),
            "points_from_prior_high": None if not prior or prior["high"] is None else round(edge - prior["high"], 2),
            "points_from_prior_low": None if not prior or prior["low"] is None else round(edge - prior["low"], 2),
            "points_from_prior_close": None if not prior or prior["close"] is None else round(edge - prior["close"], 2),
            "points_from_prior_vah": None if not value or value["vah"] is None else round(edge - value["vah"], 2),
            "points_from_prior_val": None if not value or value["val"] is None else round(edge - value["val"], 2),
            "points_from_prior_poc": None if not value or value["poc"] is None else round(edge - value["poc"], 2),
            # flow and state: signed for the fade (positive = flow with the fade's side)
            "delta_30s_with_fade": int((signed[k] - signed[k30]) * s) if k30 < k else 0,
            "delta_120s_with_fade": int((signed[k] - signed[k120]) * s) if k120 < k else 0,
            "approach_points_30s": round(float(px[k] - px[k30]) * -s, 2) if k30 < k else 0.0,
            "approach_points_120s": round(float(px[k] - px[k120]) * -s, 2) if k120 < k else 0.0,
            "big_orders_into_level_60s": int((big_sign[b60] == -s).sum()),
            "big_orders_with_fade_60s": int((big_sign[b60] == s).sum()),
            # labels
            "label_outcome": touch["label_outcome"],
            "label_dip_points": round(touch["label_dip_points"], 2),
        }
        for minutes in (5, 15, 30):
            j = int(np.searchsorted(t, min(at + minutes * MINUTE, end)))
            seg = px[k:j] if j > k else px[k : k + 1]
            row[f"label_mfe_{minutes}"] = round(float(seg.max() - edge) if long else float(edge - seg.min()), 2)
            row[f"label_mae_{minutes}"] = round(float(edge - seg.min()) if long else float(seg.max() - edge), 2)
        # the paper's deployed trade: limit inside the level, its stop and target, cancelled after thirty minutes
        entry = edge - s * PAPER_ENTRY_INSIDE
        j_cancel = int(np.searchsorted(t, at + PAPER_CANCEL_MIN * MINUTE))
        window = px[k:j_cancel]
        reach = np.flatnonzero(window <= entry) if long else np.flatnonzero(window >= entry)
        if reach.size == 0:
            row["label_paper_filled"], row["label_paper_r"] = False, None
        else:
            f = k + int(reach[0])
            after = px[f:]
            stop_hit = np.flatnonzero(after <= entry - PAPER_STOP) if long else np.flatnonzero(after >= entry + PAPER_STOP)
            target_hit = np.flatnonzero(after >= entry + PAPER_TARGET) if long else np.flatnonzero(after <= entry - PAPER_TARGET)
            a = int(stop_hit[0]) if stop_hit.size else None
            b = int(target_hit[0]) if target_hit.size else None
            row["label_paper_filled"] = True
            if a is None and b is None:
                row["label_paper_r"] = round(float((after[-1] - entry) * s) / PAPER_STOP, 3)
            elif b is None or (a is not None and a < b):
                row["label_paper_r"] = -1.0
            else:
                row["label_paper_r"] = round(PAPER_TARGET / PAPER_STOP, 3)
        rows.append(row)
        past.append(touch["label_outcome"])
        last_touch[touch["zone"]] = at
    return {"date": day, "covered": True, "rows": rows, "n_zones": len(zones), "seconds": round(time.monotonic() - started, 1), "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}


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
                stats["zones"] += result["n_zones"]
                for row in result["rows"]:
                    sink.write(json.dumps(row) + "\n")
                    stats["touches"] += 1
                    stats[row["label_outcome"]] += 1
                if done % 25 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(dates), "touches": stats["touches"], "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    n = max(1, stats["sessions"])
    summary = {"schema": "sires-zone-population-v1", "n_dates_requested": len(dates), "n_dates_complete": done, "sessions_covered": stats["sessions"], "sessions_not_covered": len(uncovered), "failures": failures, "touches": stats["touches"], "touches_per_session": round(stats["touches"] / n, 1), "zones_per_session": round(stats["zones"] / n, 1), "held_share": round(stats["held"] / max(1, stats["touches"]), 3), "broke_share": round(stats["broke"] / max(1, stats["touches"]), 3), "wall_seconds": round(time.monotonic() - started, 1), "workers": args.workers, "zone_rule": {"min_lots": ZONE_MIN_LOTS, "min_contracts": ZONE_MIN_CONTRACTS, "leave_points": LEAVE_POINTS}}
    (args.out / "POPULATION.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"event": "population_complete", **{k: v for k, v in summary.items() if k != "failures"}, "n_failures": len(failures)}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
