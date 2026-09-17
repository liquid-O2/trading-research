#!/usr/bin/env python3
"""Generate Sires' aggression boxes from order-level prints and fit them to the
boxes he drew on the dated sessions.

The author's levels are clusters of aggressive orders ("sixty, eighty, a
hundred contracts hitting in seconds"; the NY AM Big Trades filter is a
minimum of 30 contracts, BIG p.3) that were absorbed at one area. Our trade
file holds fills; an aggressor order is the set of fills sharing one event
timestamp and side (see the round-8 report, 10.1). A box is a cluster of such
orders close in price and time.

For each dated Sires session this script: aggregates fills to orders, keeps
orders of ``--min-size`` contracts and more, clusters them (orders within
``--band`` points and ``--window`` minutes of each other, at least
``--min-orders`` orders), and reports, per drawn box in the record, whether a
generated box overlaps it before the ticket time, plus the number of generated
boxes in the session so the count can be judged against the two to five he
draws.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))
EXAMPLES = WORKTREE / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"
TRADES = Path("/workspace/data/quantpad/cme__nq-continuous-futures__trades")
ET = ZoneInfo("America/New_York")
NS = 1_000_000_000


def ns_at(day: str, hhmm: str, offset_days: int = 0) -> int:
    d = date.fromisoformat(day) + timedelta(days=offset_days)
    h, m = int(hhmm[:2]), int(hhmm[3:5])
    return int(datetime(d.year, d.month, d.day, h, m, tzinfo=ET).timestamp() * NS)


def et(ns: int) -> str:
    return datetime.fromtimestamp(ns / NS, tz=timezone.utc).astimezone(ET).strftime("%H:%M:%S")


def week_file(day: str) -> Path:
    d = date.fromisoformat(day)
    monday = d - timedelta(days=d.weekday())
    return TRADES / f"{monday.isoformat()}.parquet"


def orders_between(day: str, start_ns: int, end_ns: int):
    """Aggressor orders in [start, end): fills grouped by (event timestamp, side)."""
    path = week_file(day)
    if not path.exists():
        return None
    table = pq.read_table(path)
    col = table["t"]
    sub = table.filter(pc.and_(pc.greater_equal(col, start_ns), pc.less(col, end_ns))).to_pandas()
    if sub.empty:
        return sub
    grouped = sub.groupby(["t", "side"], sort=True).agg(size=("size", "sum"), lo=("price", "min"), hi=("price", "max"), fills=("size", "count")).reset_index()
    return grouped


def adaptive_big(orders, *, quantile: float, lookback_s: int, floor: int):
    """Orders whose size sits in the top ``1 - quantile`` of the aggressor orders
    of the trailing ``lookback_s`` seconds (causal; the author adjusts the
    bubble scale "with the session's volume", BIG p.3). ``floor`` keeps a
    quiet overnight from admitting five-lot orders as big trades."""
    import numpy as np
    o = orders.sort_values("t").reset_index(drop=True)
    t = o["t"].to_numpy()
    size = o["size"].to_numpy()
    keep = np.zeros(len(o), dtype=bool)
    thresholds = np.zeros(len(o))
    left = 0
    for i in range(len(o)):
        while t[left] < t[i] - lookback_s * NS:
            left += 1
        window = size[left:i] if i > left else size[:1]
        thr = max(float(np.quantile(window, quantile)) if len(window) >= 50 else float(floor), float(floor))
        thresholds[i] = thr
        keep[i] = size[i] >= thr
    o = o.assign(threshold=thresholds)
    return o[keep]


def minute_range_median(orders, at_ns: int, lookback_s: int = 1800) -> float:
    """The median one-minute range of the trailing half hour, from the orders' prices."""
    import numpy as np
    sub = orders[(orders["t"] >= at_ns - lookback_s * NS) & (orders["t"] < at_ns)]
    if sub.empty:
        return 5.0
    minute = (sub["t"] // (60 * NS))
    g = sub.groupby(minute).agg(lo=("lo", "min"), hi=("hi", "max"))
    r = (g["hi"] - g["lo"]).to_numpy()
    return float(np.median(r)) if len(r) else 5.0


def cluster_orders(orders, *, min_size: int, band: float, window_s: int, min_orders: int, adaptive: dict | None = None) -> list[dict]:
    if adaptive:
        big = adaptive_big(orders, quantile=adaptive["quantile"], lookback_s=adaptive["lookback_s"], floor=adaptive["floor"]).sort_values("t")
    else:
        big = orders[orders["size"] >= min_size].sort_values("t")
    boxes: list[dict] = []
    for _, row in big.iterrows():
        placed = False
        for box in boxes:
            near_price = row["lo"] <= box["hi"] + band and row["hi"] >= box["lo"] - band
            near_time = row["t"] - box["last_t"] <= window_s * NS
            if near_price and near_time:
                box["lo"] = min(box["lo"], float(row["lo"]))
                box["hi"] = max(box["hi"], float(row["hi"]))
                box["last_t"] = int(row["t"])
                box["orders"].append({"t": int(row["t"]), "size": int(row["size"]), "side": row["side"], "lo": float(row["lo"]), "hi": float(row["hi"])})
                placed = True
                break
        if not placed:
            boxes.append({"lo": float(row["lo"]), "hi": float(row["hi"]), "first_t": int(row["t"]), "last_t": int(row["t"]), "orders": [{"t": int(row["t"]), "size": int(row["size"]), "side": row["side"], "lo": float(row["lo"]), "hi": float(row["hi"])}]})
    out = []
    for box in boxes:
        if len(box["orders"]) < min_orders:
            continue
        sides = {o["side"] for o in box["orders"]}
        largest_order = max(box["orders"], key=lambda o: o["size"])
        aggressor = largest_order["side"] if largest_order["side"] in ("A", "B") else "B"
        out.append({"lo": box["lo"], "hi": box["hi"], "first": et(box["first_t"]), "last": et(box["last_t"]), "known_at": box["last_t"], "n_orders": len(box["orders"]), "contracts": sum(o["size"] for o in box["orders"]), "sides": "".join(sorted(sides)), "largest": max(o["size"] for o in box["orders"]), "aggressor": aggressor})
    return out


def absorbed(orders, boxes: list[dict], *, follow_s: int, give: float, give_in_ranges: bool = False) -> list[dict]:
    """Keep the boxes whose aggression was ABSORBED: within ``follow_s`` seconds
    after the last order, price does not travel more than ``give`` points
    beyond the box in the aggressor's direction ("buyers keep pricing in and
    keep getting absorbed into the catalyst", OFM p.7). The check reads the
    trade prices themselves."""
    out = []
    t = orders["t"].to_numpy()
    lo = orders["lo"].to_numpy()
    hi = orders["hi"].to_numpy()
    for box in boxes:
        a, b = box["known_at"], box["known_at"] + follow_s * NS
        mask = (t > a) & (t <= b)
        if not mask.any():
            continue
        if box["aggressor"] == "B":
            excursion = float(hi[mask].max()) - box["hi"]
        else:
            excursion = box["lo"] - float(lo[mask].min())
        # the tolerance follows the tape: ``give`` is a multiple of the trailing
        # half hour's median one-minute range when ``give_in_ranges`` is set
        allowed = give * minute_range_median(orders, box["known_at"]) if give_in_ranges else give
        box = {**box, "follow_through": round(excursion, 2), "allowed": round(allowed, 2), "absorbed": excursion <= allowed}
        if box["absorbed"]:
            out.append(box)
    return out


def box_type(name: str) -> str:
    """What the author drew: an aggression / absorption / refill box (order-flow
    prints), a squeeze structure (the failure box, the wick, the entry box) or
    a profile object (nodes, resistance, support, composite, balance)."""
    n = name.lower()
    if any(k in n for k in ("aggression", "absorb", "refill", "pm_box")):
        return "aggression"
    if any(k in n for k in ("failure", "squeeze", "wick", "entry_box")):
        return "structure"
    return "profile"


def drawn_boxes(example: dict) -> list[dict]:
    out = []
    for name, value in (example.get("levels") or {}).items():
        if isinstance(value, list) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
            lo, hi = sorted(value)
            if hi - lo <= 30:  # a box, not a dealing range or balance
                out.append({"name": name, "lo": float(lo), "hi": float(hi), "type": box_type(name)})
        elif isinstance(value, list) and value and all(isinstance(v, list) and len(v) == 2 for v in value):
            for i, pair in enumerate(value):
                lo, hi = sorted(pair)
                if hi - lo <= 30:
                    out.append({"name": f"{name}[{i}]", "lo": float(lo), "hi": float(hi), "type": box_type(name)})
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-size", type=int, default=30)
    parser.add_argument("--band", type=float, default=6.0)
    parser.add_argument("--window", type=int, default=180, help="seconds between orders of one box")
    parser.add_argument("--min-orders", type=int, default=2)
    parser.add_argument("--from", dest="from_hhmm", default="08:00")
    parser.add_argument("--absorbed", action="store_true", help="keep only boxes whose aggression got no follow-through")
    parser.add_argument("--adaptive", action="store_true", help="size cut = trailing-hour quantile of order sizes; absorption tolerance = give x trailing median minute range")
    parser.add_argument("--quantile", type=float, default=0.995)
    parser.add_argument("--lookback", type=int, default=3600)
    parser.add_argument("--floor", type=int, default=20)
    parser.add_argument("--follow", type=int, default=180, help="seconds after the last order to test for follow-through")
    parser.add_argument("--give", type=float, default=4.0, help="points beyond the box the aggressor may get and still count as absorbed")
    args = parser.parse_args(argv)
    examples = [e for e in json.loads(EXAMPLES.read_text())["examples"] if e["id"].startswith("SI") and e.get("inside_tape")]
    report = []
    for ex in examples:
        day = ex["date"]
        tickets = [a for a in ex.get("actions") or [] if a.get("proper_entry")]
        if not tickets:
            continue
        first_ticket = min(str(a["time_et"])[:5] for a in tickets)
        overnight = int(first_ticket[:2]) < 8
        if overnight:
            start = ns_at(day, "18:00", -1)
            end = ns_at(day, "03:00")
        else:
            start = ns_at(day, args.from_hhmm)
            end = ns_at(day, "11:00")
        orders = orders_between(day, start, end)
        if orders is None:
            report.append({"id": ex["id"], "error": f"no trade file {week_file(day).name}"})
            print(json.dumps(report[-1]))
            continue
        adaptive = {"quantile": args.quantile, "lookback_s": args.lookback, "floor": args.floor} if args.adaptive else None
        boxes = cluster_orders(orders, min_size=args.min_size, band=args.band, window_s=args.window, min_orders=args.min_orders, adaptive=adaptive)
        n_raw = len(boxes)
        if args.absorbed:
            boxes = absorbed(orders, boxes, follow_s=args.follow, give=args.give, give_in_ranges=args.adaptive)
        drawn = drawn_boxes(ex)
        matches = []
        for d in drawn:
            hits = [b for b in boxes if b["lo"] <= d["hi"] + 3 and b["hi"] >= d["lo"] - 3]
            matches.append({"drawn": d["name"], "lo": d["lo"], "hi": d["hi"], "generated": [{"lo": b["lo"], "hi": b["hi"], "first": b["first"], "last": b["last"], "n": b["n_orders"], "contracts": b["contracts"], "sides": b["sides"]} for b in hits[:3]]})
        for m, d in zip(matches, drawn):
            m["type"] = d["type"]
        n_matched = sum(1 for m in matches if m["generated"])
        by_type = {}
        for m in matches:
            bt = by_type.setdefault(m["type"], [0, 0])
            bt[1] += 1
            bt[0] += 1 if m["generated"] else 0
        row = {"id": ex["id"], "window": f"{et(start)}-{et(end)}", "orders_ge_min": int((orders["size"] >= args.min_size).sum()), "generated_boxes": len(boxes), "raw_boxes": n_raw, "drawn_boxes": len(drawn), "drawn_matched": n_matched, "by_type": by_type, "matches": matches, "boxes": boxes}
        report.append(row)
        print(json.dumps({"id": ex["id"], "orders>=min": row["orders_ge_min"], "raw": n_raw, "generated": len(boxes), "drawn": len(drawn), "matched": n_matched, "by_type": by_type, "unmatched": [f'{m["drawn"]}({m["type"][:4]})' for m in matches if not m["generated"]]}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "SIRES_LEVELS_FIT.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
    total_drawn = sum(r.get("drawn_boxes", 0) for r in report if "error" not in r)
    total_matched = sum(r.get("drawn_matched", 0) for r in report if "error" not in r)
    totals = {}
    for r in report:
        for k, (m, n) in (r.get("by_type") or {}).items():
            t = totals.setdefault(k, [0, 0]); t[0] += m; t[1] += n
    gen = [r.get("generated_boxes", 0) for r in report if "error" not in r]
    print(json.dumps({"event": "fit_complete", "drawn": total_drawn, "matched": total_matched, "by_type": totals, "generated_per_session_mean": round(sum(gen) / len(gen), 1) if gen else None, "params": vars(args) | {"out": str(args.out)}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
