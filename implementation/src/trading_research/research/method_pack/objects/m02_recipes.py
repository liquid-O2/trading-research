"""FORMULAS M02 object recipes used by the GB-FAIL vertical slice.

The M02 method reuses the reviewed C01 observation foundations (O001--O004
and O029) registered by ``m01_recipes``.  The registrations below are the
Green Bird specific objects.  They deliberately keep literal geometry and
source supplied qualitative interpretations separate: a computed price
relation may be available while a source detector remains a hole.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register


DAY = date(2026, 1, 15)


def _d(hour: int, minute: int = 0) -> int:
    return et_ns(DAY, hour, minute)


def _r(recipe_id: str, state: str, value: dict, **kwargs) -> RecipeResult:
    return RecipeResult(recipe_id, state, value, **kwargs)


def _invalid(recipe_id: str, value: dict, *, reason: str = "causal") -> RecipeResult:
    return _r(recipe_id, "invalid", value, base_ok=False, coverage_ok=True, reason=reason)


@register("O046", ("end_ns",))
def o046(inp: dict) -> RecipeResult:
    """Freeze a complete source session/hour and test a later boundary sweep.

    ``members`` is accepted for real time-bar/event inputs.  The compact H/L
    spelling is retained for the printed numerical fixture.  In both cases a
    range is not available before its half-open formation end.
    """

    from trading_research.research.method_pack.clocks import range_hl

    end = inp["end_ns"]
    use_at = inp.get("use_at", end)
    members = inp.get("members")
    invalid_reason = None
    if members is not None:
        try:
            got = range_hl(members, inp.get("start_ns", 0), end, use_at)
        except (TypeError, ValueError) as exc:
            got = {"available": False, "H": None, "L": None,
                   "W": None, "known_at": None, "invalid": str(exc)}
        complete = bool(got.get("available"))
        high, low = got.get("H"), got.get("L")
        invalid_reason = got.get("invalid")
        known_at = got.get("known_at")
    else:
        high = dec(inp.get("H"))
        low = dec(inp.get("L"))
        complete = use_at >= end and not inp.get("missing_row")
        known_at = end if complete else None
        if high is None or low is None:
            complete = False
            invalid_reason = "missing_price"
        elif high <= low:
            complete = False
            invalid_reason = "non_positive_width"
        elif use_at < end:
            invalid_reason = "pre_end_use"
        elif inp.get("missing_row"):
            invalid_reason = "incomplete_or_missing_member"

    width = None if high is None or low is None else high - low
    source_session = inp.get("session_id", inp.get("source_session_id"))
    boundary_ids = inp.get("boundary_ids")
    if boundary_ids is None:
        boundary_ids = ([f"{source_session}:high", f"{source_session}:low"]
                        if source_session else [])

    price = dec(inp.get("price"))
    price_at = inp.get("price_at")
    can_sweep = None
    if price is not None and price_at is not None and high is not None:
        can_sweep = bool(complete and price_at >= end and price > high)
    elif complete:
        can_sweep = False

    value = {
        "box_high": high,
        "box_low": low,
        "box_width": width,
        "formation_end": end,
        "known_at": known_at,
        "boundary_ids": boundary_ids,
        "source_session_id": source_session,
        "complete": complete,
        "can_sweep": can_sweep,
        # Fixture and downstream compatibility aliases.
        "H": high,
        "L": low,
        "W": width,
        "opposing_low": low,
    }
    if not complete:
        missing = []
        if members is None:
            if high is None:
                missing.append("HOLE:O046:H")
            if low is None:
                missing.append("HOLE:O046:L")
        holes = missing or ["HOLE:O046:coverage"]
        base_ok = False if (price_at is not None and price_at < end and inp.get("claim_sweep")) else None
        return _r("O046", "hole", value, hole_ids=holes,
                  known_at=known_at, base_ok=base_ok, coverage_ok=None,
                  reason=invalid_reason or "incomplete_or_missing_member")
    return _r("O046", "computed", value, known_at=known_at,
              base_ok=True, coverage_ok=True, reason=invalid_reason)


@register("O049", ("tdo",))
def o049(inp: dict) -> RecipeResult:
    """Keep midnight TDO distinct from cash/evening opens and optional."""

    tdo = dec(inp["tdo"])
    cash_open = dec(inp.get("cash_open"))
    evening_open = dec(inp.get("evening_open"))
    required = inp.get("tdo_required")
    close = dec(inp.get("confirm_close"))
    side = inp.get("side")
    if required is None:
        return _r("O049", "hole", {
            "tdo_price": tdo, "tdo_known_at": inp.get("tdo_known_at", inp.get("known_at")),
            "close_through_tdo": None, "source_tdo_close_confirmed": None,
            "applicability": None,
        }, hole_ids=["HOLE:O049:applicability"],
                  known_at=inp.get("known_at"), base_ok=None, coverage_ok=None,
                  reason="selected TDO role unavailable")

    if required is True:
        missing = []
        if close is None:
            missing.append("HOLE:O049:confirm_close")
        if side not in {"short", "long"}:
            missing.append("HOLE:O049:side")
        complete_bar = inp.get("complete_clock_five_minute_bar")
        if complete_bar is None:
            missing.append("HOLE:O049:complete_clock_five_minute_bar")
        if missing:
            return _r("O049", "hole", {
                "tdo_price": tdo,
                "tdo_known_at": inp.get("tdo_known_at", inp.get("known_at")),
                "close_through_tdo": None,
                "source_tdo_close_confirmed": None,
                "applicability": "required",
                "tdo": tdo, "cash_open": cash_open, "evening_open": evening_open,
                "distinct": None if cash_open is None or evening_open is None
                            else len({tdo, cash_open, evening_open}) == 3,
                "complete_clock_five_minute_bar": complete_bar,
            }, hole_ids=missing, known_at=inp.get("known_at"),
                      base_ok=None, coverage_ok=None,
                      reason="required TDO confirmation unavailable")

    distinct = None
    if cash_open is not None and evening_open is not None:
        distinct = len({tdo, cash_open, evening_open}) == 3
    if required is False:
        return _r("O049", "computed", {
            "tdo_price": tdo,
            "tdo_known_at": inp.get("tdo_known_at", inp.get("known_at")),
            "close_through_tdo": None,
            "source_tdo_close_confirmed": None,
            "applicability": "not_required",
            "tdo": tdo, "cash_open": cash_open, "evening_open": evening_open,
            "distinct": distinct,
        }, applicability="not_required", known_at=inp.get("known_at"),
                  base_ok=True, coverage_ok=True)

    close_through = None
    if close is not None:
        close_through = close < tdo if side == "short" else close > tdo if side == "long" else None
    elif side not in {"short", "long"}:
        close_through = None
    if inp.get("complete_clock_five_minute_bar") is False:
        close_through = False
    return _r("O049", "computed", {
        "tdo_price": tdo,
        "tdo_known_at": inp.get("tdo_known_at", inp.get("known_at")),
        "close_through_tdo": close_through,
        "source_tdo_close_confirmed": close_through,
        "applicability": "required",
        "tdo": tdo, "cash_open": cash_open, "evening_open": evening_open,
        "distinct": distinct,
        "complete_clock_five_minute_bar": inp.get("complete_clock_five_minute_bar"),
    }, known_at=inp.get("known_at"), base_ok=True, coverage_ok=True)


@register("O051", ("friday_close", "sunday_open"))
def o051(inp: dict) -> RecipeResult:
    """Construct a supplied new-week gap without choosing its convention."""

    friday = dec(inp["friday_close"])
    sunday = dec(inp["sunday_open"])
    convention = inp.get("friday_convention", inp.get("endpoint_convention"))
    if convention is None:
        return _r("O051", "hole", {
            "gap": [friday, sunday], "gap_lo": min(friday, sunday),
            "gap_hi": max(friday, sunday), "gap_width": abs(sunday - friday),
            "automatic_gap": None,
        }, hole_ids=["HOLE:O051:endpoint_convention"],
                  known_at=inp.get("known_at"), base_ok=None, coverage_ok=None,
                  reason="Friday close convention unavailable")
    lo, hi = min(friday, sunday), max(friday, sunday)
    price = dec(inp.get("price"))
    has_gap = friday != sunday
    if price is None:
        full_fill = partial = None
    elif not has_gap:
        full_fill = partial = False
    else:
        # The Friday edge is the full-fill destination.  The opposite edge
        # is a contact with the gap, so both edges are inclusive for contact
        # measurement when a nonzero gap exists.
        full_fill = price <= friday if sunday > friday else price >= friday
        partial = bool(lo <= price <= hi and price != friday)
    value = {
        "gap": [lo, hi], "gap_lo": lo, "gap_hi": hi,
        "gap_width": hi - lo, "width": hi - lo,
        "known_at": inp.get("known_at"),
        "partial_contact": partial, "full_fill": full_fill,
        "entered": partial, "filled": full_fill,
        "automatic_gap": has_gap,
    }
    return _r("O051", "computed", value, known_at=inp.get("known_at"),
              base_ok=True, coverage_ok=True)


@register("O052", ("H", "L", "impulse_side"))
def o052(inp: dict) -> RecipeResult:
    """Compute the source-measured 50--61.8% impulse retracement."""

    high, low = dec(inp["H"]), dec(inp["L"])
    width = high - low
    if width <= 0:
        return _r("O052", "invalid", {"width": width, "band": None,
                                       "touch": None, "failure_from_touch": None},
                  hole_ids=["HOLE:O052:impulse_width"], base_ok=False,
                  coverage_ok=None, reason="non_positive_width")
    side = inp["impulse_side"]
    if side == "down":
        band = [low + Decimal("0.50") * width,
                low + Decimal("0.618") * width]
    elif side == "up":
        band = [high - Decimal("0.618") * width,
                high - Decimal("0.50") * width]
    else:
        return _r("O052", "hole", {"width": width, "band": None,
                                    "touch": None, "failure_from_touch": None},
                  hole_ids=["HOLE:O052:impulse_direction"], base_ok=None,
                  coverage_ok=None, reason="impulse direction unavailable")
    price = dec(inp.get("price"))
    touch = None if price is None else band[0] <= price <= band[1]
    return _r("O052", "computed", {
        "width": width, "band": band,
        "band_lo": band[0], "band_hi": band[1],
        "touch": touch,
        "failure_from_touch": False,
        "linked_failure_id": inp.get("linked_failure_id"),
    }, known_at=inp.get("known_at"), base_ok=True, coverage_ok=True)


@register("O053", ("L", "H", "price"))
def o053(inp: dict) -> RecipeResult:
    """Compute literal range position and preserve a separate VWAP relation."""

    low, high, price = dec(inp["L"]), dec(inp["H"]), dec(inp["price"])
    width = high - low
    if width <= 0:
        return _r("O053", "invalid", {"midpoint": None, "position": None,
                                       "location": None},
                  hole_ids=["HOLE:O053:range_width"], base_ok=False,
                  coverage_ok=None, reason="non_positive_width")
    midpoint = (low + high) / 2
    location = "discount" if price < midpoint else "premium" if price > midpoint else "equilibrium"
    vwap = dec(inp.get("vwap"))
    vs_vwap = None if vwap is None else ("above" if price > vwap else "below" if price < vwap else "at")
    return _r("O053", "computed", {
        "midpoint": midpoint,
        "range_mid": midpoint,
        "position": (price - low) / width,
        "normalized_position": (price - low) / width,
        "location": location,
        "vs_vwap": vs_vwap,
        "relations_must_agree": False,
    }, known_at=inp.get("known_at"), base_ok=True, coverage_ok=True)


@register("O054", ("failure_at", "swing_confirmed_at", "break_at"))
def o054(inp: dict) -> RecipeResult:
    """Audit a supplied MSS-after-failure ordering; detector remains a hole."""

    failure_at = inp["failure_at"]
    swing_at = inp["swing_confirmed_at"]
    break_at = inp["break_at"]
    entry_at = inp.get("entry_at")
    order_ok = failure_at < swing_at <= break_at and (entry_at is None or break_at <= entry_at)
    if entry_at is not None and entry_at < failure_at:
        return _invalid("O054", {"order_ok": False, "automatic_mss": None}, reason="causal")
    source_mss = inp.get("source_mss_confirmed")
    value = {
        "structure_reference": inp.get("structure_reference", inp.get("swing_id")),
        "structure_confirmation_at": swing_at,
        "failure_at": failure_at, "break_at": break_at, "entry_at": entry_at,
        "order_ok": order_ok,
        "mss_after_failure": source_mss,
        "automatic_mss": None,
    }
    if not order_ok:
        return _invalid("O054", value, reason="causal")
    if source_mss is None:
        return _r("O054", "hole", value,
                  known_at=inp.get("known_at", entry_at or break_at),
                  hole_ids=["HOLE:O054:source_mss_confirmed"], base_ok=True,
                  coverage_ok=None, reason="source MSS confirmation unavailable")
    return _r("O054", "supplied", value,
              known_at=inp.get("known_at", entry_at or break_at),
              base_ok=True, coverage_ok=True)


@register("O059", ("necessary_ok",))
def o059(inp: dict) -> RecipeResult:
    """Audit the necessary Green Bird sweep condition without grading."""

    necessary = inp["necessary_ok"]
    label = inp.get("supplied_label", inp.get("source_grade"))
    if necessary is False:
        grade_ok = False
    else:
        grade_ok = None
    holes = [] if grade_ok is False else ["HOLE:O059:grade_engine"]
    return _r("O059", "supplied" if grade_ok is False else "hole", {
        "source_grade": label,
        "necessary_grade_condition_ok": necessary,
        "grade_ok": grade_ok,
        "automatic_grade": None,
        "unpublished_grade_fields": ["sufficient_grade_conditions"],
        "grade_known_at": inp.get("known_at"),
        "early_is_confirmed_refill": False if inp.get("early_entry") else None,
        "small_size": inp.get("small_size"),
    }, known_at=inp.get("known_at"), hole_ids=holes,
              base_ok=True, coverage_ok=None if holes else True,
              reason=None if not holes else "unpublished grade engine")


@register("O136", ("bias_at",))
def o136(inp: dict) -> RecipeResult:
    """Retain a source directional read and reject retrospective causality."""

    bias_at = inp["bias_at"]
    direction = inp.get("direction", inp.get("bias_side"))
    origin = inp.get("origin_reference_id")
    if direction is None or origin is None:
        holes = []
        if direction is None:
            holes.append("HOLE:O136:direction")
        if origin is None:
            holes.append("HOLE:O136:origin_reference_id")
        return _r("O136", "hole", {
            "bias_recorded": None,
            "bias_side": direction,
            "bias_start": inp.get("bias_start", bias_at),
            "bias_known_at": bias_at,
            "origin_reference_id": origin,
            "direction": direction,
            "later_event_explains_bias": None,
            "automatic_bias_selector": None,
        }, known_at=bias_at, hole_ids=holes, base_ok=None,
                  coverage_ok=None, reason="direction or origin evidence unavailable")
    candidate_side = inp.get("candidate_side")
    if candidate_side is not None and candidate_side != direction:
        return _invalid("O136", {
            "bias_recorded": False,
            "bias_side": direction,
            "bias_start": inp.get("bias_start", bias_at),
            "bias_known_at": bias_at,
            "origin_reference_id": origin,
            "direction": direction,
            "candidate_side": candidate_side,
            "later_event_explains_bias": False,
            "automatic_bias_selector": None,
        }, reason="identity mismatch")
    use_at = inp.get("use_at")
    if use_at is not None and bias_at > use_at:
        return _invalid("O136", {"bias_recorded": False,
                                  "bias_known_at": bias_at}, reason="causal")
    later = inp.get("later_event_at")
    return _r("O136", "supplied", {
        "bias_recorded": True,
        "bias_side": direction,
        "bias_start": inp.get("bias_start", bias_at),
        "bias_known_at": bias_at,
        "origin_reference_id": origin,
        "revision_history": inp.get("revision_history", []),
        "direction": direction,
        "later_event_explains_bias": False,
        "later_event_at": later,
        "automatic_bias_selector": None,
    }, known_at=bias_at, base_ok=True, coverage_ok=True)


# These are the printed object fixtures from the M02 section.  The protocol
# expands each one into late, missing and identity mutations using the
# required tuples above; mutations therefore exercise the real dependency
# guard rather than a private ``_wrong_identity`` flag.
add_fixture({
    "id": "O046-F1", "recipe": "O046",
    "inputs": {"H": 110, "L": 100, "start_ns": _d(9), "end_ns": _d(10),
               "price": 111, "price_at": _d(9, 45), "claim_sweep": True,
               "use_at": _d(9, 45), "known_at": _d(10)},
    "expected": {"can_sweep": False, "base_ok": False},
})
add_fixture({
    "id": "O046-F1b", "recipe": "O046",
    "inputs": {"H": 110, "L": 100, "start_ns": _d(9), "end_ns": _d(10),
               "price": 111, "price_at": _d(10, 5), "use_at": _d(10, 5),
               "known_at": _d(10)},
    "expected": {"can_sweep": True, "L": Decimal("100"), "complete": True},
})
add_fixture({
    "id": "O046-F1c", "recipe": "O046",
    "inputs": {"H": 110, "L": 100, "end_ns": _d(10), "missing_row": True,
               "use_at": _d(10), "known_at": _d(10)},
    "expected": {"complete": False},
})

add_fixture({
    "id": "O049-F1", "recipe": "O049",
    "inputs": {"tdo": 100, "cash_open": 105, "evening_open": 98,
               "tdo_required": True, "confirm_close": 99, "side": "short",
               "complete_clock_five_minute_bar": True,
               "known_at": _d(0), "use_at": _d(10, 5)},
    "expected": {"distinct": True, "source_tdo_close_confirmed": True},
})
add_fixture({
    "id": "O049-F1b", "recipe": "O049",
    "inputs": {"tdo": 100, "cash_open": 105, "evening_open": 98,
               "tdo_required": True, "confirm_close": 101, "side": "short",
               "complete_clock_five_minute_bar": True,
               "known_at": _d(0), "use_at": _d(10, 5)},
    "expected": {"source_tdo_close_confirmed": False},
})
add_fixture({
    "id": "O049-F1c", "recipe": "O049",
    "inputs": {"tdo": 100, "cash_open": 105, "evening_open": 98,
               "tdo_required": False, "known_at": _d(0), "use_at": _d(10, 5)},
    "expected": {"applicability": "not_required"},
})

add_fixture({
    "id": "O051-F1", "recipe": "O051",
    "inputs": {"friday_close": 100, "sunday_open": 104,
               "friday_convention": "prior_rth_close", "price": 102,
               "known_at": _d(18), "use_at": _d(18, 1)},
    "expected": {"gap": [Decimal("100"), Decimal("104")],
                 "width": Decimal("4"), "entered": True, "filled": False},
})
add_fixture({
    "id": "O051-F1b", "recipe": "O051",
    "inputs": {"friday_close": 100, "sunday_open": 104,
               "friday_convention": "prior_rth_close", "price": 100,
               "known_at": _d(18), "use_at": _d(18, 1)},
    "expected": {"filled": True},
})
add_fixture({
    "id": "O051-F1c", "recipe": "O051",
    "inputs": {"friday_close": 100, "sunday_open": 104,
               "known_at": _d(18), "use_at": _d(18, 1)},
    "expected": {"automatic_gap": None},
})

add_fixture({
    "id": "O052-F1", "recipe": "O052",
    "inputs": {"H": 120, "L": 100, "impulse_side": "down", "price": 111,
               "known_at": _d(10), "use_at": _d(10, 5)},
    "expected": {"band": [Decimal("110"), Decimal("112.36")], "touch": True,
                 "failure_from_touch": False},
})
add_fixture({
    "id": "O052-F1b", "recipe": "O052",
    "inputs": {"H": 120, "L": 100, "impulse_side": "up", "price": 111,
               "known_at": _d(10), "use_at": _d(10, 5)},
    "expected": {"band": [Decimal("107.64"), Decimal("110")], "touch": False},
})

add_fixture({
    "id": "O053-F1", "recipe": "O053",
    "inputs": {"L": 100, "H": 120, "price": 108, "vwap": 107,
               "known_at": _d(10), "use_at": _d(10, 1)},
    "expected": {"midpoint": Decimal("110"), "position": Decimal("0.4"),
                 "location": "discount", "vs_vwap": "above",
                 "relations_must_agree": False},
})

add_fixture({
    "id": "O054-F1", "recipe": "O054",
    "inputs": {"failure_at": _d(10, 5), "swing_confirmed_at": _d(10, 6),
               "break_at": _d(10, 7), "entry_at": _d(10, 8),
               "automatic_detector": None, "known_at": _d(10, 7),
               "use_at": _d(10, 8)},
    "expected": {"order_ok": True, "automatic_mss": None},
})
add_fixture({
    "id": "O054-F1b", "recipe": "O054",
    "inputs": {"failure_at": _d(10, 5), "swing_confirmed_at": _d(10, 6),
               "break_at": _d(10, 7), "entry_at": _d(10, 4),
               "known_at": _d(10, 7), "use_at": _d(10, 4)},
    "expected": {"base_ok": False},
})

add_fixture({
    "id": "O059-F1", "recipe": "O059",
    "inputs": {"necessary_ok": False, "supplied_label": "A+",
               "automatic_grade": None, "known_at": _d(10, 6),
               "use_at": _d(10, 6)},
    "expected": {"grade_ok": False},
})
add_fixture({
    "id": "O059-F1b", "recipe": "O059",
    "inputs": {"necessary_ok": True, "automatic_grade": None,
               "early_entry": True, "known_at": _d(10, 6),
               "use_at": _d(10, 6)},
    "expected": {"automatic_grade": None, "early_is_confirmed_refill": False},
})

add_fixture({
    "id": "O136-F1", "recipe": "O136",
    "inputs": {"direction": "long", "bias_at": _d(9, 15),
               "origin_reference_id": "source-origin-2026-01-15",
               "use_at": _d(9, 40), "later_event_at": _d(10, 5),
               "known_at": _d(9, 15)},
    "expected": {"bias_recorded": True, "later_event_explains_bias": False},
})
add_fixture({
    "id": "O136-F1b", "recipe": "O136",
    "inputs": {"direction": "long", "bias_at": _d(9, 15),
               "origin_reference_id": "source-origin-2026-01-15",
               "use_at": _d(9, 10), "known_at": _d(9, 15)},
    "expected": {"base_ok": False},
})
