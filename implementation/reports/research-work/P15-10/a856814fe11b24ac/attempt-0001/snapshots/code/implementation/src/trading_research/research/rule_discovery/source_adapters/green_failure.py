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
