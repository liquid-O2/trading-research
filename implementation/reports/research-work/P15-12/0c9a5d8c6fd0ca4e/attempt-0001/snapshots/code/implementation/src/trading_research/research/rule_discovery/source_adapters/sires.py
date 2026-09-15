"""P15-12 Sires thesis and flow branches."""
from __future__ import annotations

from typing import Any

from trading_research.research.rule_discovery.baseline_repairs import _thesis_direction
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dual_scan,
    scan_family_date,
)

FAMILY = "SIRES"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("P1", "P6", "C5", "three_tick_replenishment", "ofm_1r_3r")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-12",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "adapter_rules": {
            "P1": "compare effort with the immediately preceding equal-duration window; empty counts as zero",
            "P6": "dedup key-gamma contacts on reference_lifecycle_id",
            "C5": "thesis direction from larger-balance half, None on the midpoint",
            "replenishment": "three-tick passive replenishment filter",
            "ofm": "1R to 3R objective",
        },
    }


def independent_thesis_direction(micro: dict | None, htf: dict | None) -> int | None:
    """C5 operational rule, labelled as such."""
    return _thesis_direction(micro, htf)


def three_tick_replenishment(passive_ticks: int) -> bool:
    return int(passive_ticks) >= 3


def ofm_objective_r(entry: int, stop: int, r_multiple: int) -> int:
    width = abs(int(entry) - int(stop))
    if r_multiple not in {1, 2, 3}:
        raise ValueError("OFM objective is 1R, 2R or 3R")
    return width * int(r_multiple)


def four_stage_order() -> tuple[str, ...]:
    return ("locate", "provoke", "absorb", "continue")


def swapped_middle_rejected(stages: tuple[str, ...]) -> bool:
    return stages != four_stage_order()


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-12"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    return payload
