"""FORMULAS M06 object delta and printed fixtures."""

from __future__ import annotations

from decimal import Decimal

from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register
from trading_research.research.method_pack.objects.rest_recipes import _d, _r


@register("O089", ("entry", "stop", "target", "asia_range"))
def o089(inp: dict) -> RecipeResult:
    entry, stop, target = dec(inp["entry"]), dec(inp["stop"]), dec(inp["target"])
    stop_d = abs(stop - entry)
    tgt_d = abs(entry - target)
    asia = dec(inp["asia_range"])
    known = inp.get("range_known_at", inp.get("known_at"))
    decision = inp.get("decision_at", inp.get("use_at"))
    if (not all(value.is_finite() for value in (entry, stop, target, asia))
            or asia <= 0 or stop_d == 0):
        return _r("O089", "invalid", {
            "stop_distance": stop_d, "target_distance": tgt_d,
            "source_range_reference": asia, "source_ambition_ok": None,
            "automatic_target": None, "universal_rule": False,
        }, known_at=known, base_ok=False, coverage_ok=None,
            hole_ids=["HOLE:O089:geometry"], reason="invalid ticket or source range geometry")
    if known is None or decision is None:
        return _r("O089", "hole", {
            "stop_distance": stop_d, "target_distance": tgt_d,
            "source_range_reference": asia, "source_ambition_ok": None,
            "automatic_target": None, "universal_rule": False,
        }, known_at=known, base_ok=None, coverage_ok=None,
            hole_ids=["HOLE:O089:known_at"], reason="source range availability is unknown")
    if known > decision or inp.get("framework") == "sires_overnight":
        return _r("O089", "invalid", {
            "stop_distance": stop_d, "target_distance": tgt_d,
            "source_range_reference": asia, "source_ambition_ok": None,
            "automatic_target": None, "universal_rule": False,
        }, known_at=known, base_ok=False, coverage_ok=None,
            hole_ids=["HOLE:O089:source_context"],
            reason="future range or foreign overnight framework substituted")
    ambition = inp.get("source_ambition_ok")
    rationale = inp.get("source_rationale")
    holes = [] if rationale is not None and ambition is not None else ["HOLE:O089:selector"]
    return _r("O089", "computed" if not holes else "hole", {
        "stop_distance": stop_d,
        "target_distance": tgt_d,
        "source_range_reference": asia,
        "asia_range": asia,
        "target_over_asia": tgt_d / asia,
        "source_ambition_ok": ambition if rationale is not None else None,
        "ambition_classification": None if rationale is None else inp.get("ambition"),
        "automatic_target": None,
        "universal_rule": False,
    }, known_at=known, base_ok=True, coverage_ok=True if not holes else None,
        hole_ids=holes, reason=None if not holes else "source ambition selector is unpublished")


@register("O094", ("orig_lo", "orig_hi", "explore_at", "failure_at", "return_at",
                   "reaccept_at", "control_at", "decision_at"))
def o094(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["orig_lo"]), dec(inp["orig_hi"])
    names = ("explore_at", "failure_at", "return_at", "reaccept_at", "control_at", "decision_at")
    stages = [inp[name] for name in names]
    original_id = inp.get("original_balance_id")
    tested_id = inp.get("tested_value_id")
    identity_invalid = original_id is not None and tested_id is not None and original_id == tested_id
    geometry_invalid = not lo.is_finite() or not hi.is_finite() or lo >= hi
    order = all(left < right for left, right in zip(stages, stages[1:]))
    value = {
        "route_ok": bool(order and not identity_invalid and not geometry_invalid),
        "original": [lo, hi],
        "original_balance_id": original_id,
        "tested_value_id": tested_id,
        **{name: inp[name] for name in names},
    }
    if geometry_invalid or identity_invalid or not order:
        reason = ("source area identity mismatch" if identity_invalid else
                  "invalid original balance geometry" if geometry_invalid else
                  "failed-auction stages are not strictly ordered")
        return _r("O094", "invalid", value, known_at=inp["decision_at"],
                  base_ok=False, coverage_ok=None, hole_ids=["HOLE:O094:sequence"], reason=reason)
    holes = [f"HOLE:O094:{field}" for field, value_ in (
        ("original_balance_id", original_id), ("tested_value_id", tested_id)) if value_ is None]
    return _r("O094", "supplied" if not holes else "hole", value,
              known_at=inp["decision_at"], base_ok=True,
              coverage_ok=True if not holes else None, hole_ids=holes,
              reason=None if not holes else "source area identity is unavailable")


add_fixture({"id": "O089-F1", "recipe": "O089", "inputs": {"entry": 110, "stop": 112, "target": 105, "asia_range": 8, "known_at": _d(4, 0), "use_at": _d(9, 40)}, "expected": {"stop_distance": Decimal("2"), "target_distance": Decimal("5"), "target_over_asia": Decimal("0.625"), "ambition_classification": None, "universal_rule": False}})


add_fixture({"id": "O094-F1", "recipe": "O094", "inputs": {"orig_lo": 100, "orig_hi": 110, "explore_at": _d(9, 40), "failure_at": _d(9, 50), "return_at": _d(10, 0), "reaccept_at": _d(10, 5), "control_at": _d(10, 7), "decision_at": _d(10, 8), "known_at": _d(9, 20), "use_at": _d(10, 8)}, "expected": {"route_ok": True}})


add_fixture({"id": "O094-F1b", "recipe": "O094", "inputs": {"orig_lo": 100, "orig_hi": 110, "explore_at": _d(9, 40), "failure_at": _d(9, 50), "return_at": _d(10, 0), "reaccept_at": _d(10, 5), "control_at": _d(10, 7), "decision_at": _d(9, 55), "known_at": _d(9, 20), "use_at": _d(9, 55)}, "expected": {"route_ok": False, "base_ok": False}})
