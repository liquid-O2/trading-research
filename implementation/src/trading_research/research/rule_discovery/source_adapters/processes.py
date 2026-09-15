"""P15-16 research-process and risk observations, including F-REFILL-POP."""
from __future__ import annotations

from typing import Any

import numpy as np

from trading_research.research.rule_discovery.native import NativeMarketView, NS
from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
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
CLUSTER_MIN_SIZE = 80
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
                "cluster_min_size": CLUSTER_MIN_SIZE,
                "source": "refill-effect.pdf pp.5-9 chart caption >=40 and clustered aggressive prints in seconds",
                "label": "source_inspired",
                "population_scale_unreconciled": True,
                "resolution_path": "ii",
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
        armed = False
        last_touch = None
        for j in range(later_idx.size):
            px = int(later_ticks[j])
            ts = int(later_t[j])
            outside = px >= hi + dep if zone["side"] == "long" else px <= lo - dep
            inside = lo <= px <= hi
            if not armed:
                if outside:
                    armed = True
                continue
            if inside:
                if last_touch is None or ts > last_touch:
                    out.append(
                        {
                            "zone_formed_at_ns": formed,
                            "departure_at_ns": ts,
                            "touch_at_ns": ts,
                            "side": zone["side"],
                        }
                    )
                    last_touch = ts
                    armed = False
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


REFILL_UNRECONCILED_REASON = (
    "pre-registration ordering cannot be established in this environment: git commands "
    "are forbidden, so a committed tolerance hash cannot be cited; the registered "
    "2024-12-01 to 2025-11-30 260-session hold/R/dip replay was not re-run; any "
    "touches/session figure measured on the 9-date engineering slice is not the "
    "registered 260-session window. REFILL-STUDY remains population_scale_unreconciled."
)


def reconcile_population(n_touches: int, n_sessions: int) -> dict[str, Any]:
    rate = (n_touches / n_sessions) if n_sessions else 0.0
    order = PRINTED_TOUCHES_PER_SESSION
    within = 0.5 * order <= rate <= 2.0 * order
    return {
        "n_touches": n_touches,
        "n_sessions": n_sessions,
        "touches_per_session": rate,
        "printed_touches_per_session": order,
        "order_of_magnitude": within,
        "population_kind": "engineering_slice",
        "population_scale_unreconciled": True,
        "registered_window_sessions": 260,
        "registered_window": {"start": "2024-12-01", "end": "2025-11-30"},
        "resolution_path": "ii",
        "reason": REFILL_UNRECONCILED_REASON,
        "slice_order_of_magnitude_not_reconciliation": True,
    }


def no_entry_denominator(unit: str) -> bool:
    return unit in {"process", "research", "personal", "risk"}


def amt_states_are_not_day_types() -> tuple[str, ...]:
    return ("B", "A", "D", "E", "W")


def native_bbo_cannot_certify_ten_level() -> bool:
    return True


def _departure_before_touch(market, *, lo, hi, zone_known_at: int, touch_at: int):
    """Last complete bar outside the band by DEPARTURE_TICKS before touch. False if none, unknown if the window is unobservable."""
    from decimal import Decimal

    from trading_research.research.method_pack.historical_features import Q

    if touch_at <= zone_known_at:
        return None, False
    dep = Q * DEPARTURE_TICKS
    lo_d, hi_d = Decimal(str(lo)), Decimal(str(hi))
    try:
        bars = list(market.bars(int(zone_known_at), int(touch_at)))
    except (TypeError, ValueError, AttributeError):
        return None, None
    complete = None
    if hasattr(market, "coverage"):
        try:
            cov = market.coverage(int(zone_known_at), int(touch_at))
            if cov is not None:
                complete = bool(cov.get("observed_scope_complete"))
        except (TypeError, ValueError, AttributeError):
            complete = None
    if not bars:
        return None, None if complete is not False else False
    last = None
    for row in bars:
        start = row.get("start")
        if start is None or int(start) >= int(touch_at):
            continue
        low, high = row.get("L"), row.get("H")
        if low is None or high is None:
            continue
        low_d, high_d = Decimal(str(low)), Decimal(str(high))
        if low_d > hi_d + dep or high_d < lo_d - dep:
            last = row.get("known_at") or row.get("end") or start
    if last is None:
        return None, False if complete is not False else None
    last_i = int(last)
    if not (int(zone_known_at) < last_i < int(touch_at)):
        return last_i, False
    return last_i, True


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Touch-causality clocks from formation freeze, pre-touch departure, and the contact."""
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        bounds,
        contact_as_trigger,
        contact_side,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    complete = bool(trigger.get("observed_complete") or trigger.get("complete") or contact.get("complete", True))
    touch_at = contact.get("at_ns") or trigger.get("start")
    decision = trigger.get("known_at") or trigger.get("end") or contact.get("available_at_ns")
    ok = True if complete else None
    if branch != "touch_record":
        values = {
            "branch": branch,
            "side": side,
            "source_confirmation": ok,
            "confirm_at": decision if ok else None,
            "decision_at": decision,
            "location_touched": True,
            "distinct_touch_id": True,
        }
        return {"values": values, "confirm_at": values["confirm_at"], "decision_at": decision, "cutoff_ns": decision, "source_confirmation": ok}

    ref = scanner_ref(reference, formation)
    lo, hi = bounds(ref)

    def _first_clock(*values):
        for item in values:
            if item is not None:
                return int(item)
        return None

    zone_known_at = _first_clock(
        (formation or {}).get("available_at_ns"),
        (reference or {}).get("issue_at_ns"),
        ref.get("known_at"),
        (formation or {}).get("end_ns"),
    )
    departure_at, departed = (None, None)
    if zone_known_at is not None and touch_at is not None and lo is not None and hi is not None:
        departure_at, departed = _departure_before_touch(
            market, lo=lo, hi=hi, zone_known_at=int(zone_known_at), touch_at=int(touch_at)
        )
    elif zone_known_at is None or touch_at is None:
        departed = None
    else:
        departed = None
    feature_clocks = [int(zone_known_at)] if zone_known_at is not None else []
    prior_resolved: list[int] = []
    feature_max_known_at = max(feature_clocks) if feature_clocks else None
    memory_ok = None if touch_at is None else all(int(item) < int(touch_at) for item in prior_resolved)
    pre_touch = [clock for clock in (zone_known_at, departure_at, feature_max_known_at) if clock is not None]
    label_ok = None if touch_at is None else all(int(clock) <= int(touch_at) for clock in pre_touch)
    values = {
        "branch": branch,
        "side": side,
        "zone_definition_recorded": True if lo is not None and hi is not None and zone_known_at is not None else None,
        "zone_frozen": True if zone_known_at is not None else None,
        "zone_known_at": None if zone_known_at is None else int(zone_known_at),
        "instrument_and_threshold_preserved": True if getattr(market, "instrument_id", None) is not None else None,
        "departure_observed": departed,
        "departure_at": departure_at,
        "distinct_touch_id": True,
        "touch_at": touch_at,
        "thesis_recorded": True,
        "feature_max_known_at": feature_max_known_at,
        "memory_uses_only_prior_resolved_touches": memory_ok,
        "label_uses_only_post_touch_observations": label_ok,
        "source_confirmation": ok if departed is not False else False,
        "confirm_at": decision if ok else None,
        "decision_at": decision,
        "location_touched": True,
    }
    return {"values": values, "confirm_at": values["confirm_at"], "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


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
        "population_kind": "engineering_slice",
        "population_scale_unreconciled": True,
        "refill_reason": REFILL_UNRECONCILED_REASON,
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
