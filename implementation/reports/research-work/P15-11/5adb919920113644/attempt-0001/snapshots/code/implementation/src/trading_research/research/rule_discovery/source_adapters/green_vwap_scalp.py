"""P15-11 Green Bird VWAP and scalp configurations."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dual_scan,
    golden_pocket,
    scan_family_date,
)

FAMILY_VWAP = "GB-VWAP"
FAMILY_SCALP = "GB-SCALP"
FINDINGS = ("D1", "A4")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "families": [FAMILY_VWAP, FAMILY_SCALP],
        "task_id": "P15-11",
        "branches": {
            FAMILY_VWAP: list(FAMILY_BRANCHES[FAMILY_VWAP]),
            FAMILY_SCALP: list(FAMILY_BRANCHES[FAMILY_SCALP]),
        },
        "source_additions": ["golden_pocket_continuation"],
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
    }


def d1_retest_window_explanation() -> dict[str, Any]:
    """Why every GB-VWAP rejection became unknown under D1.

    Frozen scan_green_vwap line 314 rebinds continuation_context with the
    retest-absence answer, discarding the True computed at line 308. Every
    census rejection in the audited pool is this overwrite: a missing later
    VWAP return flips the already-true breakout-context conjunct to false,
    so the recorded rejection reason is not the retest window. B0.1 keeps
    continuation_context as the breakout comparison and records retest_at
    separately. The source retest window is the declared one-hour horizon
    after the breakout, not a rewrite of breakout context.
    """
    return {
        "finding": "D1",
        "frozen_symbol": "historical_price_scanners.scan_green_vwap",
        "lines": "308-then-314",
        "mechanism": "continuation_context rebound to retest-absence",
        "effect": "every GB-VWAP rejection in the audited pool is this artifact",
        "retest_window": "breakout_end to min(session_end, breakout_end+60m)",
        "b01": "continuation_context stays the breakout conjunct; retest_at is separate",
        "example": "2023-12-08",
        "fixture": "test_p15_11.py::test_d1_retest_window_does_not_overwrite_breakout_context",
    }


def golden_pocket_continuation(low: Decimal, high: Decimal, side: str) -> dict[str, Any]:
    lo, hi = golden_pocket(low, high)
    if side == "short":
        lo, hi = golden_pocket(high, low) if high < low else (lo, hi)
    return {
        "branch": "golden_pocket_continuation",
        "addition": "A4",
        "band": [str(lo), str(hi)],
        "entry": "first complete five-minute close back out of the pocket in impulse direction",
        "entry_label": "operational",
        "stop": "beyond the far edge of the pocket",
        "clock_zone_unverified": True,
        "custom_not_source_long": True,
    }


def slice_family(day: str) -> dict[str, Any]:
    vwap = scan_family_date(day, FAMILY_VWAP, FAMILY_BRANCHES[FAMILY_VWAP])
    scalp = scan_family_date(day, FAMILY_SCALP, FAMILY_BRANCHES[FAMILY_SCALP])
    return {
        "date": day,
        "task_id": "P15-11",
        "vwap": vwap,
        "scalp": scalp,
        "d1": d1_retest_window_explanation(),
        "clock_zone_unverified": True,
        "wall_seconds": float(vwap.get("wall_seconds") or 0) + float(scalp.get("wall_seconds") or 0),
        "peak_rss_bytes": max(int(vwap.get("peak_rss_bytes") or 0), int(scalp.get("peak_rss_bytes") or 0)),
        "native_executions": vwap.get("native_executions"),
        "populations": {
            "B0": _merge(vwap["populations"]["B0"], scalp["populations"]["B0"]),
            "B0.1": _merge(vwap["populations"]["B0.1"], scalp["populations"]["B0.1"]),
        },
    }


def _merge(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    keys = set(a) | set(b)
    return {key: int(a.get(key, 0)) + int(b.get(key, 0)) for key in keys}
