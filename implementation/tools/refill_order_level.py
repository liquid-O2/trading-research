#!/usr/bin/env python3
"""Refill re-measurement: zones and touches per session from aggressor ORDERS
(fills grouped by event timestamp and side) against the fill-level zones the
B0.2 scan formed, on a set of native sessions. The paper's printed figures
(REF pp.5-8): 41,152 touches over 235 sessions (175 a session), hold rate
0.42. Output: one JSON row per session with zone counts, touch counts and hold
rates for both constructions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

from trading_research.research.rule_discovery.source_adapters import refill_b02 as rb  # noqa: E402
from trading_research.research.rule_discovery.source_adapters.common import load_source_market  # noqa: E402


def measure(day: str) -> dict:
    market = load_source_market(day)
    view = rb._as_view(market)
    arrays = view.arrays
    cutoff = int(arrays.known_at_ns.max())
    out = {"session": day}
    for name, formed in (("fills", rb.form_b02_zones(view)), ("orders", rb.form_b02_zones_orders(view))):
        touches = 0
        holds = 0
        labelled = 0
        for zone in formed["zones"]:
            zone_known = int(zone.get("known_at_ns") or zone["formed_at_ns"])
            dep = rb.actual_departure_ns(arrays, zone, cutoff)
            if dep is None:
                continue
            for touch in rb.touches_after_departure(arrays, zone, dep, cutoff):
                touch_at = int(touch["touch_at_ns"])
                if max(zone_known, int(dep)) > touch_at:
                    continue
                touches += 1
                hold = rb.hold_label(arrays, zone, touch_at, cutoff)
                if hold is not None:
                    labelled += 1
                    holds += int(hold)
        out[name] = {"prints": formed["n_prints"], "zones": formed["n_zones"], "touches": touches, "hold_rate": None if not labelled else round(holds / labelled, 3), "orders": formed.get("n_orders")}
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", required=True, help="comma-separated native sessions")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    rows = []
    for day in args.days.split(","):
        row = measure(day)
        rows.append(row)
        print(json.dumps(row), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "REFILL_ORDER_LEVEL.json").write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
