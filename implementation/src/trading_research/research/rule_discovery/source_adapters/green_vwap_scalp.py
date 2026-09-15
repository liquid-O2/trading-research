"""P15-11 Green Bird VWAP and scalp configurations."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping

from trading_research.research.contracts.types import RuleSpec

from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    dual_scan,
    golden_pocket,
    scan_family_date,
)
from trading_research.research.rule_discovery.source_adapters.green_b02 import (
    RULES as B02_RULES,
    replay_example as gb_replay_example,
    scan_b02 as gb_scan_b02,
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


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Later VWAP retest (GB-VWAP) or the pullback bar (GB-SCALP)."""
    from trading_research.research.method_pack.historical_features import MINUTE, Q
    from trading_research.research.rule_discovery.source_adapters.confirmation import contact_as_trigger, px, scanner_ref

    trigger = contact_as_trigger(market, contact)
    family = "GB-VWAP" if branch == "source_long" else "GB-SCALP"
    if family == "GB-SCALP":
        decision = trigger.get("known_at") or trigger.get("end")
        values = {
            "branch": branch,
            "side": contact.get("side") or "long",
            "source_confirmation": True if trigger.get("observed_complete") else None,
            "confirm_at": decision,
            "decision_at": decision,
            "location_touched": True,
        }
        return {"values": values, "confirm_at": decision, "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}
    deadline = min(int(market.end), int(trigger["end"]) + 60 * MINUTE)
    retest = None
    vw = None
    for row in market.bars(trigger["end"], deadline):
        snapshot = market.vwap(row["start"])
        if snapshot.get("price") is not None and row["L"] <= snapshot["price"] <= row["H"]:
            retest = row
            vw = snapshot
            break
    from trading_research.research.rule_discovery.baseline_repairs import absent_repaired

    missing_retest = None if retest is not None else absent_repaired(market, trigger["end"], deadline)
    decision = retest["known_at"] if retest else deadline
    stop = retest["L"] - Q if retest else None
    entry = retest["C"] if retest else None
    asia = (reference or {}).get("asia")
    london = (reference or {}).get("london")
    if asia is None or london is None:
        from trading_research.research.method_pack.branch_coverage import setting

        sessions = setting("gb_sessions")
        asia_lo, asia_hi = sessions["asia"]
        london_lo, london_hi = sessions["london"]
        asia = market.range(market.at(asia_lo, -1 if asia_lo >= "18:00" else 0), market.at(asia_hi), "asia")
        london = market.range(market.at(london_lo, -1 if london_lo >= "18:00" else 0), market.at(london_hi), "london")
    ref_ok = asia is not None and london is not None
    values = {
        "branch": branch,
        "side": "long",
        "reference_frozen": bool(ref_ok),
        "london_high": None if london is None else px(london.get("high")),
        "london_known_at": None if london is None else london.get("known_at"),
        "asia_high": None if asia is None else px(asia.get("high")),
        "asia_known_at": None if asia is None else asia.get("known_at"),
        "continuation_context": True if trigger.get("C") is not None and ref_ok and px(trigger["C"]) > max(px(asia["high"]), px(london["high"])) else None,
        "breakout_at": trigger.get("known_at") or trigger.get("end"),
        "breakout_close": px(trigger.get("C")),
        "vwap_reset_verified": True,
        "vwap_known_at": None if vw is None else vw.get("known_at"),
        "vwap_at_retest": None if vw is None else vw.get("price"),
        "retest_at": None if retest is None else retest.get("known_at"),
        "retest_low": None if retest is None else retest.get("L"),
        "retest_high": None if retest is None else retest.get("H"),
        "risk_defined": (entry > stop) if entry is not None and stop is not None else (False if missing_retest is False else None),
        "decision_at": decision,
        "source_confirmation": True if retest is not None else missing_retest,
        "confirm_at": decision if retest is not None else None,
    }
    return {"values": values, "confirm_at": values["confirm_at"], "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


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
        "population_kind": "engineering_slice",
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


RULES = {key: value for key, value in B02_RULES.items() if key.startswith(("F01", "F13", "F06-A4", "RR-14", "RR-12", "F07"))}


def scan_b02(market, rec: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(rec or {})
    payload.setdefault("family", FAMILY_VWAP)
    return gb_scan_b02(market, payload)


def replay_example(market, example: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(example)
    if "GB-SCALP" in str(payload.get("family") or "") and "VWAP" not in str(payload.get("family") or ""):
        payload["family"] = FAMILY_SCALP
    else:
        payload.setdefault("family", FAMILY_VWAP)
    return gb_replay_example(market, payload)
