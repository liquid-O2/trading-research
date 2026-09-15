"""P15-10 Green Bird failure branches."""
from __future__ import annotations

from typing import Any, Mapping

from trading_research.research.method_pack.historical_price_scanners import _gb_refs
from trading_research.research.rule_discovery.baseline_repairs import scan_green_failure_repaired
from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    dual_scan,
    empty_delta_spec,
    enumerate_own_population,
    scan_family_date,
)

FAMILY = "GB-FAIL"
BRANCHES = FAMILY_BRANCHES[FAMILY]
SOURCE_ADDITIONS = ("london_box", "asia_box", "overnight_scan", "golden_pocket", "entry_on_retracement")
FINDINGS = ("P4", "C3", "A1", "A2", "A3")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-10",
        "branches": list(BRANCHES),
        "source_additions": list(SOURCE_ADDITIONS),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "p4": "empty sweep path is an availability omission, not a raise",
    }


def london_box_window() -> dict[str, str]:
    return {"start": "02:00", "end": "05:00", "clock": "A2-GB-CLOCK", "addition": "A1"}


def asia_box_window() -> dict[str, str]:
    return {"start": "20:00", "end": "00:00", "tdo_required": False, "addition": "A2"}


def overnight_scan_branches() -> tuple[str, ...]:
    return (
        "prior_day_level",
        "prior_week_level",
        "prior_month_level",
        "asia_tdo_case",
        "asia_box",
        "london_box",
    )


def prior_period_unknown_not_substitute(missing: bool) -> str:
    return "unknown" if missing else "complete"


def sweep_and_reclaim_not_collapsed(sweep_at: int, reclaim_at: int | None) -> bool:
    if reclaim_at is None:
        return True
    return reclaim_at >= sweep_at


def scan_addition(market, name: str) -> dict[str, Any]:
    if name == "london_box":
        ref = market.range(market.at("02:00"), market.at("05:00"), "london-box")
        begin = None if ref is None else ref["known_at"]
        return {
            "branch": "london_box",
            "addition": "A1",
            "reference": None if ref is None else {"id": ref["id"], "low": str(ref["low"]), "high": str(ref["high"]), "known_at": ref["known_at"]},
            "scan_start_ns": begin,
            "scan_end_ns": market.end,
            "clock_zone_unverified": True,
            "population": "own",
            "tdo_required": False,
            "pocket_required": False,
        }
    if name == "asia_box":
        ref = market.range(market.at("20:00", -1), market.at("00:00"), "asia-box")
        return {
            "branch": "asia_box",
            "addition": "A2",
            "reference": None if ref is None else {"id": ref["id"], "low": str(ref["low"]), "high": str(ref["high"])},
            "tdo_required": False,
            "clock_zone_unverified": True,
            "population": "own",
        }
    if name == "overnight_scan":
        return {
            "addition": "A3",
            "branches": list(overnight_scan_branches()),
            "accepted_start": "09:30",
            "added_start": "reference_known_at",
            "reported_separately": True,
            "clock_zone_unverified": True,
        }
    raise ValueError(name)


def p4_empty_path_omission() -> dict[str, Any]:
    return {
        "finding": "P4",
        "frozen": "ValueError on empty sweep path",
        "adapter": "availability omission",
        "b01": "scan_green_failure_repaired",
    }


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """First complete five-minute reclaim at or after the contact, as B0.1 C3."""
    from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        contact_as_trigger,
        contact_side,
        range_frozen,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    sg = sign(side)
    ref = scanner_ref(reference, formation)
    boundary = ref["high"] if side == "short" else ref["low"]
    aligned = int(trigger["start"]) // (5 * MINUTE) * (5 * MINUTE)
    end = int(market.end)
    confirm = None
    close = None
    usable = False
    confirmation_end = aligned + 5 * MINUTE
    offset = 0
    while True:
        bar_start = aligned + offset * 5 * MINUTE
        bar_end = bar_start + 5 * MINUTE
        if bar_start >= end:
            break
        cand = market.bars(bar_start, bar_end, 300)
        row = cand[0] if cand else None
        ok_bar = row is not None and row.get("observed_complete") and row.get("C") is not None
        if ok_bar and boundary is not None and sg * (row["C"] - boundary) > 0:
            confirm = row
            close = row["C"]
            usable = True
            confirmation_end = bar_end
            break
        if ok_bar and confirm is None:
            confirm = row
            close = row["C"]
            usable = True
            confirmation_end = bar_end
        offset += 1
    excursion = market.bars(trigger["start"], confirmation_end) or [trigger]
    high = max(r["H"] for r in excursion)
    low = min(r["L"] for r in excursion)
    stop = high + Q if side == "short" else low - Q
    target = ref["low"] if side == "short" else ref["high"]
    inside = None if close is None or ref["low"] is None or ref["high"] is None else (
        ref["low"] < close < ref["high"] if ref["low"] != ref["high"] else True
    )
    pre = market.range(market.at("06:00"), min(max(int(market.at("09:30")), int(ref.get("known_at") or 0)), market.at("09:30")), "gb-precontext")
    context_known = pre is not None and pre["known_at"] <= trigger["start"]
    tdo_required = branch == "asia_tdo_case"
    tdo_rows = market.bars(market.at("00:00"), market.at("00:00") + MINUTE)
    tdo = tdo_rows[0]["O"] if tdo_rows else None
    touch = contact.get("at_ns") or trigger["start"]
    values = {
        "branch": branch,
        "side": side,
        "reference_frozen": range_frozen(ref),
        "reference_known_at": ref.get("known_at"),
        "reference_px": boundary,
        "bias_recorded": context_known,
        "context_at": pre["known_at"] if pre else None,
        "source_session_allowed": True,
        "sweep_at": touch,
        "sweep_high": high,
        "sweep_low": low,
        "confirmation_mode": "five_minute_close",
        "complete_clock_five_minute_bar": True if usable else None,
        "confirm_at": confirmation_end if confirm else None,
        "confirm_close": close,
        "box_return_ok": inside,
        "tdo_required": tdo_required,
        "source_tdo_close_confirmed": None if tdo is None or close is None else sg * (close - tdo) > 0,
        "pocket_required": False,
        "retracement_entry": False,
        "risk_defined": None if close is None else sg * (close - stop) > 0,
        "objective_fixed": None if close is None or target is None else sg * (target - close) > 0,
        "decision_at": confirmation_end,
        "source_confirmation": None if close is None else bool(inside) if inside is not None else (sg * (close - boundary) > 0 if boundary is not None else None),
    }
    return {
        "values": values,
        "confirm_at": values["confirm_at"],
        "decision_at": confirmation_end,
        "cutoff_ns": confirmation_end,
        "source_confirmation": values["source_confirmation"],
    }


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-10"
    payload["source_additions"] = list(SOURCE_ADDITIONS)
    payload["p4"] = p4_empty_path_omission()
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["population_kind"] = "engineering_slice"
    return payload
