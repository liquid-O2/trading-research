"""P15-16 research-process and risk observations, including F-REFILL-POP."""
from __future__ import annotations

from typing import Any

import numpy as np

from trading_research.research.rule_discovery.native import NativeMarketView, NS
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    scan_family_date,
)

FAMILY_REFILL = "REFILL-STUDY"
FAMILY_JET = "JETBUNDLE-STATES"
FAMILY_STOIC = "STOIC-DATA"
FAMILY_RISK = "STOIC-RISK"
PRINTED_TOUCHES_PER_SESSION = 175
# refill-effect.pdf p.5 chart caption: bubble size = contracts in the aggressive print (>=40 shown).
PRINT_THRESHOLD = 40
# Paper: "sixty, eighty, a hundred contracts hitting in seconds".
CLUSTER_SECONDS = 5
CLUSTER_SPAN_TICKS = 2
CLUSTER_MIN_PRINTS = 2
CLUSTER_MIN_SIZE = 60
DEPARTURE_TICKS = 4


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "task_id": "P15-16",
        "families": [FAMILY_REFILL, FAMILY_JET, FAMILY_STOIC, FAMILY_RISK],
        "entry_denominator": False,
        "clock_zone_unverified": True,
        "refill": {
            "finding": "F-REFILL-POP",
            "printed_touches_per_session": PRINTED_TOUCHES_PER_SESSION,
            "printed_sessions": 235,
            "printed_touches": 41152,
            "b0": {"min_event_quantity": 100, "min_events": 2, "formation_seconds": 120, "scan_start": "09:30"},
            "adapter": {
                "print_threshold": PRINT_THRESHOLD,
                "cluster_seconds": CLUSTER_SECONDS,
                "cluster_span_ticks": CLUSTER_SPAN_TICKS,
                "source": "refill-effect.pdf pp.5-9 chart caption >=40 and clustered aggressive prints in seconds",
                "label": "source_inspired",
            },
        },
    }


def form_refill_zones(view: NativeMarketView) -> dict[str, Any]:
    """Array-first zone formation from aggressive prints. Not the frozen 100-pair recipe."""
    arrays = view.arrays
    if arrays.t_ns.size == 0:
        return {"zones": [], "touches": [], "n_prints": 0, "n_zones": 0, "n_touches": 0}
    trade = arrays.is_trade & (arrays.size >= PRINT_THRESHOLD) & (arrays.side != 0)
    idx = np.flatnonzero(trade)
    n_prints = int(idx.size)
    zones: list[dict[str, Any]] = []
    if n_prints == 0:
        return {"zones": [], "touches": [], "n_prints": 0, "n_zones": 0, "n_touches": 0}
    t_ns = arrays.t_ns[idx]
    ticks = arrays.price_ticks[idx]
    size = arrays.size[idx]
    side = arrays.side[idx]
    known = arrays.known_at_ns[idx]
    cluster_ns = CLUSTER_SECONDS * NS
    used = np.zeros(idx.size, dtype=np.bool_)
    for i in range(idx.size):
        if used[i]:
            continue
        same = (side == side[i]) & (np.abs(ticks - ticks[i]) <= CLUSTER_SPAN_TICKS) & (t_ns >= t_ns[i]) & (t_ns <= t_ns[i] + cluster_ns) & (~used)
        members = np.flatnonzero(same)
        if members.size < CLUSTER_MIN_PRINTS and int(size[members].sum()) < CLUSTER_MIN_SIZE:
            continue
        used[members] = True
        lo = int(ticks[members].min())
        hi = int(ticks[members].max())
        formed_at = int(t_ns[members].max())
        known_at = int(known[members].max())
        zones.append(
            {
                "side": "long" if int(side[i]) > 0 else "short",
                "low_ticks": lo,
                "high_ticks": hi,
                "formed_at_ns": formed_at,
                "known_at_ns": known_at,
                "print_count": int(members.size),
                "size": int(size[members].sum()),
            }
        )
    touches = _touches_after_departure(arrays, zones)
    return {
        "zones": zones,
        "touches": touches,
        "n_prints": n_prints,
        "n_zones": len(zones),
        "n_touches": len(touches),
        "print_threshold": PRINT_THRESHOLD,
        "cluster_seconds": CLUSTER_SECONDS,
        "stand_in": False,
    }


def _touches_after_departure(arrays, zones: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not zones or arrays.t_ns.size == 0:
        return []
    trade = arrays.is_trade
    t_ns = arrays.t_ns
    ticks = arrays.price_ticks
    out: list[dict[str, Any]] = []
    for zone in zones:
        lo, hi = int(zone["low_ticks"]), int(zone["high_ticks"])
        formed = int(zone["formed_at_ns"])
        dep = DEPARTURE_TICKS
        later = (t_ns > formed) & trade
        if not np.any(later):
            continue
        later_idx = np.flatnonzero(later)
        later_ticks = ticks[later_idx]
        later_t = t_ns[later_idx]
        if zone["side"] == "long":
            departed = later_ticks >= hi + dep
        else:
            departed = later_ticks <= lo - dep
        if not np.any(departed):
            continue
        first_dep = int(later_t[np.flatnonzero(departed)[0]])
        after = later_t > first_dep
        in_zone = (later_ticks >= lo) & (later_ticks <= hi) & after
        touch_idx = np.flatnonzero(in_zone)
        for j in touch_idx.tolist():
            out.append(
                {
                    "zone_formed_at_ns": formed,
                    "departure_at_ns": first_dep,
                    "touch_at_ns": int(later_t[j]),
                    "side": zone["side"],
                }
            )
    return out


def python_form_refill_zones(events: list[tuple[int, int, int, int]]) -> dict[str, Any]:
    """Plain-Python oracle. events are (t_ns, ticks, size, side)."""
    prints = [row for row in events if row[2] >= PRINT_THRESHOLD and row[3] != 0]
    used = [False] * len(prints)
    zones = []
    cluster_ns = CLUSTER_SECONDS * NS
    for i, (t_ns, ticks, size, side) in enumerate(prints):
        if used[i]:
            continue
        members = []
        for j, row in enumerate(prints):
            if used[j]:
                continue
            if row[3] != side:
                continue
            if abs(row[1] - ticks) > CLUSTER_SPAN_TICKS:
                continue
            if row[0] < t_ns or row[0] > t_ns + cluster_ns:
                continue
            members.append(j)
        total = sum(prints[j][2] for j in members)
        if len(members) < CLUSTER_MIN_PRINTS and total < CLUSTER_MIN_SIZE:
            continue
        for j in members:
            used[j] = True
        lo = min(prints[j][1] for j in members)
        hi = max(prints[j][1] for j in members)
        formed = max(prints[j][0] for j in members)
        zones.append({"side": "long" if side > 0 else "short", "low_ticks": lo, "high_ticks": hi, "formed_at_ns": formed, "print_count": len(members), "size": total})
    return {"n_zones": len(zones), "zones": zones}


def reconcile_population(n_touches: int, n_sessions: int) -> dict[str, Any]:
    rate = (n_touches / n_sessions) if n_sessions else 0.0
    order = PRINTED_TOUCHES_PER_SESSION
    within = 0.5 * order <= rate <= 2.0 * order
    reason = None
    if not within:
        reason = (
            f"measured {rate:.1f} touches/session versus printed ~{order}; "
            "paper mixes NQ/MNQ (chart is MNQ, bubbles >=40 MNQ) while this tape is NQ; "
            "B0 used NQ size 100 pairs in 120s from 09:30 only"
        )
    return {
        "n_touches": n_touches,
        "n_sessions": n_sessions,
        "touches_per_session": rate,
        "printed_touches_per_session": order,
        "order_of_magnitude": within,
        "reason": reason,
    }


def no_entry_denominator(unit: str) -> bool:
    return unit in {"process", "research", "personal", "risk"}


def amt_states_are_not_day_types() -> tuple[str, ...]:
    return ("B", "A", "D", "E", "W")


def native_bbo_cannot_certify_ten_level() -> bool:
    return True


def slice_family(day: str) -> dict[str, Any]:
    refill = scan_family_date(day, FAMILY_REFILL, FAMILY_BRANCHES[FAMILY_REFILL])
    jet = scan_family_date(day, FAMILY_JET, FAMILY_BRANCHES[FAMILY_JET])
    stoic = scan_family_date(day, FAMILY_STOIC, FAMILY_BRANCHES[FAMILY_STOIC])
    risk = scan_family_date(day, FAMILY_RISK, FAMILY_BRANCHES[FAMILY_RISK])
    from trading_research.research.rule_discovery.native import build_market_view, install_write_guard

    install_write_guard()
    view = build_market_view(day, full_account_day=True)
    formed = form_refill_zones(view)
    return {
        "date": day,
        "task_id": "P15-16",
        "refill_b0_b01": refill,
        "jetbundle": jet,
        "stoic_data": stoic,
        "stoic_risk": risk,
        "refill_adapter": formed,
        "entry_denominator": False,
        "clock_zone_unverified": True,
        "amt_states": amt_states_are_not_day_types(),
        "native_bbo_ten_level": False,
        "wall_seconds": sum(float(item.get("wall_seconds") or 0) for item in (refill, jet, stoic, risk)),
        "peak_rss_bytes": max(int(item.get("peak_rss_bytes") or 0) for item in (refill, jet, stoic, risk)),
        "native_executions": refill.get("native_executions"),
        "populations": {
            "B0": refill["populations"]["B0"],
            "B0.1": refill["populations"]["B0.1"],
            "adapter_touches": formed["n_touches"],
            "adapter_zones": formed["n_zones"],
        },
    }
