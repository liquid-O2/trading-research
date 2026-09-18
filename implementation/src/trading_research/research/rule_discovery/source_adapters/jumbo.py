"""P15-09 Jumbo range branches."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence
import inspect
import json

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.historical_features import sign
from trading_research.research.method_pack.protocol import jsonable
from trading_research.research.rule_discovery.source_adapters.enumeration import (
    enumeration_point,
    enumeration_scope,
    split_b02_overrides,
)
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    dual_scan,
    enumerate_own_population,
    is_native_session,
    quadrant_locations,
    scan_family_date,
)

FAMILY = "JJ-TBR"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("C1", "C2", "C7", "A2-TBR-PROJ", "judas_strict", "judas_deferred", "outbound_exit", "single_purged_add")
LITERAL_OPERANDS = {
    "exit_window_recorded": "by_construction",
    "source_clock_verified": "by_construction",
    "source_case_verified": "by_construction",
    "location_touched": "by_construction",
    "reduced_expectations": "by_construction",
    "expansion_policy": "by_construction",
    "source_zone_known": "by_construction",
}


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-09",
        "branches": list(BRANCHES),
        "b0_1_variants": ["judas_reversal", "judas_reversal_deferred"],
        "source_additions": ["quadrant_entry", "outbound_exit_09:40", "single_purged_add_09:40-09:50"],
        "findings": list(FINDINGS),
        "literal_operands": LITERAL_OPERANDS,
        "clock_zone_unverified": True,
        "pzone_recipe": "unchanged",
    }


def outbound_expiry_ns(market, day_open_ns: int | None = None) -> int:
    """Unchanged outbound respects the 09:40 expiry."""
    return int(_at(market, "09:40"))


def one_source_opening(episode: Mapping[str, Any]) -> bool:
    values = episode.get("values") or {}
    return bool(values.get("at_rth_open") is True or values.get("at_rth_open") is False)


def quadrant_population(low: Decimal, high: Decimal, side: str, baseline_eq_only: bool) -> dict[str, Any]:
    loc = quadrant_locations(low, high, side)
    baseline = {f"{side}:eq"}
    candidate = {f"{side}:eq", f"{side}:q1", f"{side}:q3"}
    return {
        "locations": {key: str(value) for key, value in loc.items()},
        "baseline_ids": sorted(baseline),
        "candidate_ids": sorted(candidate),
        "enumeration": enumerate_own_population(baseline_ids=baseline, candidate_ids=candidate, geometry_changed=True),
        "mirrored": quadrant_locations(low, high, "short" if side == "long" else "long"),
        "source": "A2-TBR-PROJ EQ/quadrant entries",
    }


def _empty_hook(market, spec: RuleSpec, result: dict[str, Any]) -> dict[str, Any]:
    branch = spec.source_branch or "judas_reversal"
    if branch == "judas_outbound":
        result["outbound_expiry_ns"] = outbound_expiry_ns(market)
        episodes = result["b0"].get("episodes") or []
        result["one_source_opening"] = None if not episodes else all(one_source_opening(ep) for ep in episodes)
    if branch == "judas_reversal":
        deferred = dual_scan(market, FAMILY, "judas_reversal_deferred")
        result["deferred_variant"] = deferred["populations"]
        result["judas_labels"] = {"strict": "judas_reversal", "deferred": "judas_reversal_deferred"}
    result["literal_operands"] = LITERAL_OPERANDS
    result["clock_zone_unverified"] = clock_zone_unverified(FAMILY, branch)
    return result


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """O056 full-C2 at this contact. Unchanged stages from the B0.1 jumbo bind."""
    from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
    from trading_research.research.method_pack.historical_price_scanners import _context, _known
    from trading_research.research.rule_discovery.baseline_repairs import _ob_repaired
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
    lo, hi = ref.get("low"), ref.get("high")
    edge = lo if side == "long" else hi
    width = None if lo is None or hi is None else hi - lo
    target = hi if side == "long" else lo
    deadline = min(int(market.end), int(trigger["end"]) + 30 * MINUTE)
    if branch in {"judas_reversal", "judas_reversal_deferred"}:
        deadline = min(deadline, int(_at(market, "09:50")))
    if branch == "judas_outbound":
        openbars = market.bars(_at(market, "09:30"), _at(market, "09:30") + 1_000_000_000, 1)
        from trading_research.research.method_pack.historical_flow import batches

        opening = batches(market.local(_at(market, "09:30"), _at(market, "09:30") + 1_000_000_000))
        first = opening[0] if opening else None
        prices = {row["price"] for row in first[1]} if first else set()
        ok = True if len(prices) == 1 else None
        decision = max(row["known_at"] for row in first[1]) if first else trigger["end"]
        confirm = {"C": next(iter(prices)) if len(prices) == 1 else None, "known_at": decision} if first else None
        stop = (lo - Q) if side == "long" and lo is not None else (hi + Q) if hi is not None else None
        touch = first[0] if first else trigger["start"]
        if getattr(market, "reconstruct", False) and ok is None and first and openbars and openbars[0].get("O") is not None:
            ok = True
            decision = openbars[0]["known_at"]
            confirm = {"C": openbars[0]["O"], "known_at": decision}
    else:
        ok, confirm, stop, _ob = _ob_repaired(market, trigger, side, deadline)
        decision = confirm["known_at"] if confirm else deadline
        touch = contact.get("at_ns") or trigger.get("start")
    entry = confirm["C"] if confirm else None
    confirm_at = confirm["known_at"] if confirm else None
    ctx = _context(market)
    pw = ctx.get("prior_width")
    context_at = int(_at(market, "09:30"))
    if branch == "judas_outbound":
        context_fixed = ctx.get("direction") == side if ctx.get("direction") else None
    elif branch == "other_session":
        context_fixed = ref.get("close") is not None and ref.get("open") is not None
        context_at = int(ref.get("end") or context_at)
    else:
        context_fixed = None if pw is None else True
    frozen = _known(ref) if ref.get("coverage") else range_frozen(ref)
    values = {
        "branch": branch if branch != "judas_reversal_deferred" else "judas_reversal",
        "side": side,
        "range_frozen": frozen,
        "range_known_at": ref.get("known_at"),
        "context_fixed": context_fixed,
        "context_at": context_at,
        "location_touched": True,
        "touch_at": touch,
        "source_confirmation": ok,
        "confirm_at": confirm_at,
        "risk_defined": None if entry is None or stop is None else sg * (entry - stop) > 0,
        "objective_fixed": None if entry is None or target is None else sg * (target - entry) > 0,
        "decision_at": decision,
    }
    if branch == "judas_outbound":
        values["directional_context"] = context_fixed
        values["at_rth_open"] = first is not None and _at(market, "09:30") <= first[0] < _at(market, "09:30") + 1_000_000_000
        values["objective_is_selected_exhaustion"] = True if width is not None else None
        values["exit_window_recorded"] = True
    elif branch in {"judas_reversal", "judas_reversal_deferred"}:
        swept = None
        if edge is not None and trigger.get("L") is not None:
            swept = trigger["L"] < edge if side == "long" else trigger["H"] > edge
        values["reversal_context"] = None if pw is None else (width is not None and width > 0)
        values["edge_swept"] = swept
        values["sweep_at"] = touch
        values["source_time_window"] = _at(market, "09:30") <= int(touch) < _at(market, "09:50")
        values["objective_is_opposing_draw"] = True if target is not None else None
        values["entry_in_reversal_window"] = _at(market, "09:40") <= int(decision) < _at(market, "09:50")
    elif branch == "single_extended":
        values["extended_context"] = None if pw is None else True
        values["entry_at_eq_or_quadrant"] = True
        values["objective_is_range_edge"] = True
        values["reduced_expectations"] = True
    elif branch == "single_purged":
        values["purged_compressed_context"] = None if pw is None else True
        values["entry_at_eq_or_quadrant"] = True
        values["expansion_policy"] = True
    elif branch == "internal_rotation":
        values["rotation_context"] = None if pw is None else True
        values["entry_at_named_internal_or_ev_band"] = True
        values["objective_is_named_rotation_target"] = True
    elif branch == "extension_reaction":
        values["prior_expansion"] = True
        values["touch_in_source_extension_area"] = True
        values["reaction_side_confirmed"] = ok
        values["objective_is_remaining_draw"] = True
    elif branch == "other_session":
        values["source_clock_verified"] = True
        values["source_case_verified"] = True
    elif branch == "timed_pzone_reversal":
        values["source_zone_known"] = True
        values["source_time_window"] = True
        values["directed_path_recorded"] = True
        values["zone_known_at"] = ref.get("known_at")
    post_fail = None
    if branch == "judas_reversal" and not values.get("entry_in_reversal_window"):
        post_fail = "entry_outside_reversal_window"
    return {
        "values": values,
        "confirm_at": confirm_at,
        "decision_at": decision,
        "cutoff_ns": decision,
        "post_fail": post_fail,
        "source_confirmation": ok,
    }


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec, empty_hook=_empty_hook)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-09"
    payload["findings"] = list(FINDINGS)
    payload["literal_operands"] = LITERAL_OPERANDS
    payload["b0_1_judas"] = {"strict": "judas_reversal", "deferred": "judas_reversal_deferred"}
    payload["population_kind"] = "engineering_slice"
    return payload


# B0.2 source-fidelity scan. Frozen B0/B0.1 paths above are unchanged.

# ---------------------------------------------------------------------------
# B0.3 source-faithful scan, rebuilt 2026-09-17 against
# reports/research-work/reviews/FIDELITY_AUDIT_2026-09-17.md sections 1.1-1.4.
# The frozen B0/B0.1 paths above are unchanged.
#
# The object (audit 1.1): one time-based range per session read. NY is the
# 06:00-09:00 ET box frozen at 09:00 with HIGH, LOW, EQ, the 25%/75% quadrants,
# the range OPEN and CLOSE, and the projection ladder beyond the edges in units
# of the range width W. London is the 02:00-03:00 box traded 03:00-06:00 with
# identical internals.

from bisect import bisect_left

from trading_research.research.rule_discovery.source_adapters.session_levels import (
    prior_sessions,
    prior_value_area,
)
from trading_research.research.rule_discovery.source_adapters.trade_selection import (
    branch_alternatives,
    MAX_ENTRIES_PER_SESSION,
    MODE_PREFERENCE,
    select_session_trades,
)

B02_VERSION = "B0.3-2026-09-17"
NS_MINUTE = 60_000_000_000
FIVE = 5 * NS_MINUTE
TICK = Decimal("0.25")
REPLAY_LEVEL_TOLERANCE = Decimal("5")
TICKET_RISK_FALLBACK = Decimal("27")
TAPE_FIRST = date(2020, 1, 2)
OUTSIDE_TAPE = "date outside the tape"
STAGE_ORDER = ("context", "reference", "location", "trigger", "confirmation", "risk", "objective", "management")

# Audit 1.1: the ladder the author draws every day.
LADDER_MULT = (
    Decimal("0.33"),
    Decimal("0.5"),
    Decimal("0.66"),
    Decimal("1"),
    Decimal("1.33"),
    Decimal("1.66"),
    Decimal("2"),
    Decimal("2.33"),
    Decimal("2.5"),
    Decimal("2.66"),
    Decimal("3"),
)
MEAN_REVERSAL = (Decimal("0.33"), Decimal("0.66"))
EXTENSION_BAND = (Decimal("1.33"), Decimal("1.66"))

# J2: confirmation runs from the sweep, at or after 09:00; the 09:40-09:50 modal
# window is an operand, never a gate (JR p.20 sell at 09:03; 2026-01-09 09:32;
# 2026-02-24 09:33; 2026-08-28 09:30-09:32).
NY_ACTION = ("09:00", "12:00")
# The Judas raids of the 6-9 edges belong to the open: "the judas trades from
# 9:30 to the reversal window and the actual reversal trade between the 9:40
# and 9:50 ... always terminating my trading session before 10am" (TBR p.8);
# his dated Judas entries run 09:05 (a pre-open raid, 2025-10-13) to 10:10
# (2025-10-03). A raid of the edge after that is the extension or rotation
# cycle's business ("cycle 2 from there to 12:00"), not a Judas.
JUDAS_RAID_WINDOW = ("09:00", "10:15")
NY_EXTENSION_ACTION = ("10:00", "16:00")
MODAL_WINDOW = ("09:40", "09:50")
LONDON_BOX_WINDOW = ("02:00", "03:00")
LONDON_ACTION = ("02:00", "06:00")
CONFIRM_HORIZON_MIN = 30
# J5: the sweep's location is the exhaustion area -- the 0.33-0.66 band, the
# 0.5 projection, or another drawn level. Depth classes are reported for every
# episode so the population can be read by class.
DEPTH_CLASSES = ("inside_0_0.33", "band_0.33_0.66", "beyond_0.66")
# J9: the author's own break-classification table (2026-06-08, 3,249 days):
# double break leads only in the 0-0.3% range-size bin (55.5% vs 44.0%); from
# 0.3% upward the single-break cases together exceed it. The five bins are the
# author's; the crossover is read off his table, not chosen.
RANGE_BINS = (
    ("0-0.3", Decimal("0"), Decimal("0.3")),
    ("0.3-0.5", Decimal("0.3"), Decimal("0.5")),
    ("0.5-0.8", Decimal("0.5"), Decimal("0.8")),
    ("0.8-1.2", Decimal("0.8"), Decimal("1.2")),
    ("1.2+", Decimal("1.2"), None),
)
SINGLE_BREAK_MIN_BIN = Decimal("0.3")
LEVEL_COINCIDENCE = Decimal("5")
# the resting stop beyond the swept extreme on every fill (the line fills,
# the two-minute reclaim, the big print, the extension band's limit fills, the
# retest of a broken box edge) and beyond a band's far edge (the give-back
# fill); a separate constant so a rescan on the coincidence tolerance does not
# move the stops (2026-09-18: the first "coincide8" candidate moved both and
# its gain could not be attributed; the first split moved only two of the
# eight stop sites, so "coincide8-clean" and "coincide12-clean" still widened
# the stops of the line fills; every stop now reads this constant, and the
# guard test pins the roles: the tolerance is only ever compared, the stop
# distance only ever added)
STOP_BEYOND_EXTREME = Decimal("5")
#: False (default since 2026-09-18): the candidate list is every branch's opportunities,
#: uncapped, a line re-enterable (see selection_for). True restores the list of
#: 2026-09-17 (the day's play only, the segment caps, CANDIDATES_REENTER_SAME_LINE).
#: The executed list is not affected by either. Read at call time.
CANDIDATES_GATE_BY_PLAY = False
CANDIDATES_REENTER_SAME_LINE = False
# where the stop of a signature fill rests (TBR pp.27-29): "conservative", a
# tick beyond the sweep candle's extreme ("Conservative Stop Loss at the low
# of the orderblock"), the baseline; "aggressive", the midpoint of the block
# ("Aggressive Stop Loss at the midpoint of the orderblock", "at the midpoint
# of the rejection block"; p.37 "Tight Initial Stops: Using the aggressive
# stop placement"). Read at call time so a rescan can set it.
SIGNATURE_STOP = "conservative"
#: FITTED, shared with the Green Bird spike turn: the share of a tagging bar's
#: own range it must close back from the extreme it made for the turn to be
#: tradeable. See green_b02.SPIKE_GIVE_BACK for the tickets it was fitted on.
SPIKE_GIVE_BACK = Decimal("0.15")

AUTHOR_EXAMPLES_PATH = Path(__file__).resolve().parents[6] / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"

PZONE_FIXTURES: dict[str, list[dict[str, Any]]] = {
    "2026-01-02": [
        {"low": Decimal("25758"), "high": Decimal("25764"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25718"), "high": Decimal("25725"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25660"), "high": Decimal("25666"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25620"), "high": Decimal("25626"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25760"), "high": Decimal("25768"), "anchor": "10:00", "session": 2, "side": "short"},
    ],
    "2026-01-09": [
        {"low": Decimal("25655"), "high": Decimal("25665"), "anchor": "09:00", "session": 1, "target": Decimal("25850"), "side": "long"},
        {"low": Decimal("25625"), "high": Decimal("25640"), "anchor": "10:00", "session": 2},
    ],
    "2025-12-30": [
        {"low": Decimal("25785"), "high": Decimal("25795"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25740"), "high": Decimal("25750"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25677"), "high": Decimal("25687"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25630"), "high": Decimal("25640"), "anchor": "09:00", "session": 1},
    ],
    "2026-02-24": [
        {"low": Decimal("24710"), "high": Decimal("24720"), "anchor": "09:00", "session": 1},
        {"low": Decimal("25000"), "high": Decimal("25010"), "anchor": "09:00", "session": 1},
    ],
}

EVRANGE_FIXTURES = {
    "2026-08-28": {"lower": Decimal("29590"), "upper": Decimal("29724")},
    "2026-09-01": {"lower": Decimal("29058"), "upper": Decimal("29195"), "plus_50": Decimal("29290")},
}


def _d(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _as_day(market) -> date | None:
    for attr in ("account_day", "day", "session_date"):
        value = getattr(market, attr, None)
        if value is None:
            continue
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        text = str(value)[:10]
        if len(text) == 10:
            return date.fromisoformat(text)
    return None


def _at(market, hhmm: str, offset: int = 0) -> int:
    getter = getattr(market, "at", None)
    if callable(getter):
        try:
            return int(getter(hhmm, offset))
        except TypeError:
            if offset == 0:
                return int(getter(hhmm))
    day = _as_day(market)
    if day is None:
        raise ValueError("market has no day for clock conversion")
    from trading_research.research.method_pack.clocks import et_ns

    hour, minute = (int(part) for part in hhmm.split(":"))
    return int(et_ns(day + timedelta(days=offset), hour, minute))


def session_bars(market, seconds: int = 60) -> list[dict[str, Any]]:
    """One pass over the tape per resolution; every scan below slices this."""
    key = f"_jj_bars_{seconds}"
    rows = getattr(market, key, None)
    if rows is None:
        try:
            rows = list(market.bars(int(market.start), int(market.end), seconds) or [])
        except Exception:
            rows = []
        rows = [row for row in rows if row.get("start") is not None]
        rows.sort(key=lambda row: int(row["start"]))
        setattr(market, key, rows)
        setattr(market, f"{key}_starts", [int(row["start"]) for row in rows])
    return rows


def _bars(market, start: int, end: int, seconds: int = 60) -> list[dict[str, Any]]:
    if start is None or end is None or end <= start:
        return []
    rows = session_bars(market, seconds)
    if not rows:
        return []
    starts = getattr(market, f"_jj_bars_{seconds}_starts")
    lo = max(int(start), int(market.start))
    hi = min(int(end), int(market.end))
    if hi <= lo:
        return []
    return rows[bisect_left(starts, lo):bisect_left(starts, hi)]


def _span(bars: list[dict[str, Any]], known_at: int | None = None) -> dict[str, Any] | None:
    highs = [_d(row["H"]) for row in bars if row.get("H") is not None]
    lows = [_d(row["L"]) for row in bars if row.get("L") is not None]
    if not highs or not lows:
        return None
    return {
        "high": max(highs),
        "low": min(lows),
        "open": _d(bars[0].get("O")),
        "close": _d(bars[-1].get("C")),
        "known_at": known_at if known_at is not None else int(bars[-1]["known_at"]),
        "start": int(bars[0]["start"]),
        "end": int(bars[-1]["end"]),
    }


# ---------------------------------------------------------------------------
# geometry


def extension_reaction_bands(high, low, width=None) -> dict[str, Any]:
    """RR-01: o015 edge +/- [1.33, 1.66] x W."""
    from trading_research.research.method_pack.objects.range_geometry import o015

    high_d, low_d = _d(high), _d(low)
    assert high_d is not None and low_d is not None
    width_d = _d(width) if width is not None else (high_d - low_d)
    result = o015({"H": high_d, "L": low_d, "W": width_d, "coordinate_convention_verified": True, "parent_id": "jj-tbr-b03"})
    value = result.value or {}
    upper, lower = value.get("upper_band"), value.get("lower_band")
    if not upper or not lower or len(upper) < 2 or len(lower) < 2:
        return {"upper": None, "lower": None, "width": width_d, "available": False, "reason": result.reason}
    return {
        "upper": [Decimal(str(upper[0])), Decimal(str(upper[1]))],
        "lower": [Decimal(str(lower[0])), Decimal(str(lower[1]))],
        "width": width_d,
        "available": True,
    }


def mean_reversal_bands(high, low) -> dict[str, Any]:
    """Audit 1.1: the mean-reversal band, edge +/- [0.33, 0.66] x W."""
    high_d, low_d = _d(high), _d(low)
    assert high_d is not None and low_d is not None
    width_d = high_d - low_d
    return {
        "upper": [high_d + MEAN_REVERSAL[0] * width_d, high_d + MEAN_REVERSAL[1] * width_d],
        "lower": [low_d - MEAN_REVERSAL[1] * width_d, low_d - MEAN_REVERSAL[0] * width_d],
        "width": width_d,
    }


def projection_ladder(high, low) -> dict[str, str]:
    high_d, low_d = _d(high), _d(low)
    assert high_d is not None and low_d is not None
    width_d = high_d - low_d
    out: dict[str, str] = {}
    for mult in LADDER_MULT:
        out[f"plus_{mult}"] = str(high_d + mult * width_d)
        out[f"minus_{mult}"] = str(low_d - mult * width_d)
    return out


def box_geometry(market, kind: str) -> dict[str, Any] | None:
    """The time-based range with every internal the author draws on it."""
    if kind in VALUE_RANGE_WINDOW:
        return _value_range_geometry(market, kind)
    if kind == "ny":
        start, end = _at(market, "06:00"), _at(market, "09:00")
    elif kind == "london":
        if (_as_day(market) or date.min) >= LONDON_LATE_BOX_FROM:
            start, end = _at(market, LONDON_LATE_BOX[0]), _at(market, LONDON_LATE_BOX[1])
        else:
            start, end = _at(market, LONDON_BOX[0], -1), _at(market, LONDON_BOX[1])
    else:
        return None
    bars = _bars(market, start, end, 60)
    span = _span(bars, known_at=end)
    if span is None:
        return None
    low, high = span["low"], span["high"]
    width = high - low
    if width <= 0:
        return None
    return {
        "kind": kind,
        "id": f"jj-{kind}-box:{market.instrument_id}:{start}:{end}",
        "low": low,
        "high": high,
        "eq": (low + high) / 2,
        "q25": low + width / 4,
        "q75": low + width * 3 / 4,
        "range_open": span["open"],
        "range_close": span["close"],
        "width": width,
        "known_at": end,
        "window": [start, end],
        "ladder": {key: Decimal(value) for key, value in projection_ladder(high, low).items()},
        "mean_reversal": mean_reversal_bands(high, low),
        "extension": extension_reaction_bands(high, low, width),
    }


# From May 2026 his charts draw the range a second way ("testing the new NT
# studies, same ranges, different layers", 2026-05-15; "in that chart is a time
# based range", 2026-05-19): the VALUE AREA of the 06:00-09:30 profile, labelled
# "VA 0.45%" / "VA 0.28%", its POC as the middle line, and the same 33 / 66 /
# 133 / 166% projections measured from the value edges with the value width.
# 2026-05-19 prints 28,915.75 / 28,865.00 / 28,834.25: the owned profile of
# 06:00-09:30 gives exactly those three prices; 2026-05-15 prints 29,283.00 /
# 29,152.00 against the owned 29,283.50 / 29,152.50. No other window on a
# half-hour grid over the three days before comes within five points.
VALUE_RANGE_WINDOW = {"ny_value": (("06:00", 0), ("09:30", 0))}
VALUE_RANGE_ACTION = ("09:30", "16:00")
#: a value line is tested on his two New York clocks, the morning ("cycle 2 from
#: there to 12:00") and the afternoon (2026-05-15, "NY PM ... quick 80 points
#: afternoon": the +0.33 at 12:46 and the value high at 12:55 are the afternoon's
#: tests of lines the morning had crossed many times); MAX_CONTACTS_PER_LEVEL
#: distinct tests of a line in each, not a dozen a day
VALUE_RANGE_SEGMENTS = (("09:30", "12:00"), ("12:00", "16:00"))


def _value_range_geometry(market, kind: str) -> dict[str, Any] | None:
    cache = getattr(market, "_jj_value_range", None)
    if cache is None:
        cache = {}
        setattr(market, "_jj_value_range", cache)
    if kind in cache:
        return cache[kind]
    result = None
    profile = getattr(market, "profile", None)
    (from_hhmm, from_day), (to_hhmm, to_day) = VALUE_RANGE_WINDOW[kind]
    start, end = _at(market, from_hhmm, from_day), _at(market, to_hhmm, to_day)
    if callable(profile) and end <= int(market.end):
        payload = profile(start, end) or {}
        low, high, poc = _d(payload.get("val")), _d(payload.get("vah")), _d(payload.get("poc"))
        if low is not None and high is not None and high > low:
            width = high - low
            result = {
                "kind": kind,
                "id": f"jj-{kind.replace('_', '-')}:{market.instrument_id}:{start}:{end}",
                "low": low,
                "high": high,
                "eq": (low + high) / 2,
                "poc": poc,
                "q25": low + width / 4,
                "q75": low + width * 3 / 4,
                "range_open": None,
                "range_close": None,
                "width": width,
                "known_at": end,
                "window": [start, end],
                "ladder": {key: Decimal(value) for key, value in projection_ladder(high, low).items()},
                "mean_reversal": mean_reversal_bands(high, low),
                "extension": extension_reaction_bands(high, low, width),
            }
    cache[kind] = result
    return result


def range_class(width: Decimal | None, price: Decimal | None) -> dict[str, Any]:
    """J9: the author's five range-size bins, in percent of price."""
    if width is None or price is None or price <= 0:
        return {"pct": None, "bin": None, "single_break_favoured": None}
    pct = width / price * Decimal("100")
    label = RANGE_BINS[-1][0]
    for name, lo, hi in RANGE_BINS:
        if pct >= lo and (hi is None or pct < hi):
            label = name
            break
    return {"pct": pct, "bin": label, "single_break_favoured": pct >= SINGLE_BREAK_MIN_BIN}


def _open_location(open_px: Decimal | None, prior: Mapping[str, Any] | None, value: Mapping[str, Any] | None) -> str | None:
    """RR-08: where the RTH open sits against the prior day's range and value."""
    if open_px is None or not prior:
        return None
    pdh, pdl = _d(prior.get("high")), _d(prior.get("low"))
    vah = _d((value or {}).get("vah"))
    val = _d((value or {}).get("val"))
    if pdl is not None and open_px < pdl:
        return "below_pdl"
    if val is not None and open_px < val:
        return "below_val"
    if pdh is not None and open_px > pdh:
        return "above_pdh"
    if vah is not None and open_px > vah:
        return "above_vah"
    if val is not None and vah is not None and val <= open_px <= vah:
        return "inside_value"
    if pdl is not None and pdh is not None and pdl <= open_px <= pdh:
        return "inside_range"
    return None


# ---------------------------------------------------------------------------
# the drawn levels, the P-zone / EVRange generators and the day read
#
# Rebuilt by the coordinator 2026-09-17 from the source (fidelity audit §1.1,
# the author's own charts and tickets). Every level carries a ROLE: a level is
# a Judas LOCATION only if the author sweeps it (a box edge into the exhaustion
# area, an overnight / London / Asia / prior-day extreme, an EVRange line, a
# P-zone); the internals (EQ, quadrants, range open) and the prior value area
# are objectives and read inputs, never Judas locations.

LIQUIDITY_KINDS = ("onh", "onl", "london_high", "london_low", "asia_high", "asia_low", "d1_high", "d1_low", "prth_high", "prth_low")
LONDON_LIQUIDITY = ("02:00", "07:05")   # audit §1.1: liquidity sessions 02:00-07:05 and 18:00-00:05
ASIA_LIQUIDITY = ("18:00", "00:05")
# The London BOX the author trades 03:00-06:00 is the overnight range that
# closes at 03:00 (08:00 London): his printed R-Hi / R-Lo on 2025-10-06, 10-07
# and 10-08 reproduce the 20:00-03:00 range within 1.5 points on both edges and
# reproduce no 02:00-03:00 window (coordinator tape check 2026-09-17).
# The London box CLOSES AT 02:00 ET (source pass 2026-09-18): on 2025-10-08 his LOW line is
# the 20:00-02:00 low 25,027.50 and the 02:45 wick goes through it (to 03:00 the low is
# 25,026.25); the dotted vertical and the blue circles on HIGH and LOW sit at 02:00 (JR
# pp.63-64); SDRange+ prints "Session 3: 02:00" (JR p.16); his 2026-06-12 sells are at 01:41
# and 02:33 ET. On 2025-10-06, 10-07 and 10-13 the 20:00-02:00 and 20:00-03:00 ranges are the
# same, which is why the 03:00 reading passed the first check.
LONDON_BOX = ("20:00", "02:00")
LONDON_TRADE = ("02:00", "07:00")
# By June 2026 the box he draws is under an hour long (JR p.47, 2026-06-12: R-Hi 29,542.5 /
# R-Lo 29,374.5 against the tape's 29,541.25 / 29,375.00 for any start from 01:03 to 01:23
# and an end at 02:00; JR p.50, 2026-06-05: about 30,224 / 30,161 read off the chart against
# 30,228.25 / 30,163.00). The chart of 06-12 begins at 01:15 ET; the start is known only to
# that twenty-minute bracket. From the month of "testing the new NT studies" (2026-05-15).
LONDON_LATE_BOX = ("01:15", "02:00")
LONDON_LATE_BOX_FROM = date(2026, 5, 1)

# P-zones and EVRange: the author's tools are proprietary; the printed frames
# are reproduced by percentile bands of the raw-point excursion from the 09:00
# anchor price over 09:00-16:00, ranked over the prior 250 sessions
# (PZONE_EVRANGE_STUDY_2026-09-17.md §5: EVRange within 5 points on all four
# printed edges, P-zone tiers within 3-7 points of the eleven printed zones).
# They are APPROXIMATIONS of his tools and are labelled as such on every
# episode (pzone_source / evrange_source = "fitted_percentile_recipe").
EXCURSION_LOOKBACK = 250
EXCURSION_WINDOW = (540, 960)   # minutes: 09:00 -> 16:00
PZONE_TIERS = {"T1": (Decimal("0.115"), Decimal("0.175")), "T2": (Decimal("0.32"), Decimal("0.355")), "T3": (Decimal("0.55"), Decimal("0.575"))}
EVRANGE_EDGE_PCT = Decimal("0.25")
EVRANGE_PLUS_50_PCT = Decimal("0.55")

_EXCURSIONS: dict[str, dict[str, tuple[Decimal, Decimal, Decimal]]] = {}


def excursion_table(data_root: str) -> dict[str, tuple[Decimal, Decimal, Decimal]]:
    """Per session: (anchor price at 09:00, up excursion, down excursion) over
    09:00-16:00 on the front contract by volume. Read once per process from the
    owned one-minute tape; nothing is written."""
    root = str(data_root)
    if root in _EXCURSIONS:
        return _EXCURSIONS[root]
    table: dict[str, tuple[Decimal, Decimal, Decimal]] = {}
    try:
        import pyarrow.parquet as pq
        from datetime import timezone as _tz
        from zoneinfo import ZoneInfo as _Zone

        folder = Path(root) / "quantpad/cme__nq-continuous-futures__ohlcv-1m"
        ny = _Zone("America/New_York")
        by_day: dict[str, list] = {}
        for path in sorted(folder.glob("*.parquet")):
            for row in pq.read_table(path, columns=["t", "instrument_id", "o", "h", "l", "c", "v"]).to_pylist():
                at = datetime.fromtimestamp(row["t"] / 1000, _tz.utc).astimezone(ny)
                by_day.setdefault(at.strftime("%Y-%m-%d"), []).append((at.hour * 60 + at.minute, row))
        a0, a1 = EXCURSION_WINDOW
        for day, rows in by_day.items():
            volume: dict[str, float] = {}
            for _m, row in rows:
                volume[row["instrument_id"]] = volume.get(row["instrument_id"], 0.0) + float(row["v"] or 0)
            if not volume:
                continue
            front = max(volume, key=volume.get)
            pre = [row for m, row in rows if row["instrument_id"] == front and m < a0]
            post = [row for m, row in rows if row["instrument_id"] == front and a0 <= m < a1]
            if not pre or len(post) < (a1 - a0) * 0.8:
                continue
            anchor = Decimal(str(max(pre, key=lambda r: r["t"])["c"]))
            up = Decimal(str(max(r["h"] for r in post))) - anchor
            down = anchor - Decimal(str(min(r["l"] for r in post)))
            table[day] = (anchor, up, down)
    except Exception:
        table = {}
    _EXCURSIONS[root] = table
    return table


def _excursion_distributions(market) -> tuple[list[Decimal], list[Decimal]] | None:
    day = _as_day(market)
    table = excursion_table(getattr(market, "data_root", "/workspace/data"))
    if day is None or not table:
        return None
    prior = [key for key in sorted(table) if key < day.isoformat()][-EXCURSION_LOOKBACK:]
    if len(prior) < EXCURSION_LOOKBACK // 2:
        return None
    ups = sorted(table[key][1] for key in prior)
    downs = sorted(table[key][2] for key in prior)
    return ups, downs


def _quantile(values: list[Decimal], p: Decimal) -> Decimal:
    if not values:
        return Decimal(0)
    position = (len(values) - 1) * p
    low = int(position)
    high = min(low + 1, len(values) - 1)
    frac = position - low
    return values[low] + (values[high] - values[low]) * frac


def generated_pzones(market, anchor_px: Decimal | None) -> list[dict[str, Any]]:
    dist = _excursion_distributions(market)
    if dist is None or anchor_px is None:
        return []
    ups, downs = dist
    zones = []
    for tier, (k0, k1) in PZONE_TIERS.items():
        zones.append({"tier": tier, "low": anchor_px + _quantile(ups, k0), "high": anchor_px + _quantile(ups, k1), "anchor": "09:00", "side": "short", "source": "fitted_percentile_recipe"})
        zones.append({"tier": tier, "low": anchor_px - _quantile(downs, k1), "high": anchor_px - _quantile(downs, k0), "anchor": "09:00", "side": "long", "source": "fitted_percentile_recipe"})
    return zones


def generated_evrange(market, anchor_px: Decimal | None) -> dict[str, Any] | None:
    dist = _excursion_distributions(market)
    if dist is None or anchor_px is None:
        return None
    ups, downs = dist
    return {
        "lower": anchor_px - _quantile(downs, EVRANGE_EDGE_PCT),
        "upper": anchor_px + _quantile(ups, EVRANGE_EDGE_PCT),
        "plus_50": anchor_px + _quantile(ups, EVRANGE_PLUS_50_PCT),
        "source": "fitted_percentile_recipe",
    }


def drawn_levels(market, box: Mapping[str, Any] | None, *, evrange: Mapping[str, Any] | None = None, pzones: Sequence[Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Every level on the author's chart, with its role.

    role "sweep": a level the author fades when it is swept (box edges into the
    exhaustion area, ONH/ONL, London and Asia extremes, D-1..D-3 extremes, the
    prior RTH high/low, EVRange lines, P-zones). role "objective": internals and
    the prior value area, which are targets and read inputs.
    """
    out: list[dict[str, Any]] = []

    def add(kind: str, side: str, price: Decimal | None, known_at: int, role: str) -> None:
        if price is None:
            return
        out.append({"kind": kind, "side": side, "price": price, "known_at": int(known_at), "role": role})

    if box is not None:
        add("box_low", "long", box["low"], box["known_at"], "sweep")
        add("box_high", "short", box["high"], box["known_at"], "sweep")
        add("eq", "both", box["eq"], box["known_at"], "objective")
        add("q25", "both", box["q25"], box["known_at"], "objective")
        add("q75", "both", box["q75"], box["known_at"], "objective")
        add("range_open", "both", box["range_open"], box["known_at"], "objective")
    london = _span(_bars(market, _at(market, LONDON_LIQUIDITY[0]), _at(market, LONDON_LIQUIDITY[1]), 60), known_at=_at(market, LONDON_LIQUIDITY[1]))
    if london is not None:
        add("london_low", "long", london["low"], london["known_at"], "sweep")
        add("london_high", "short", london["high"], london["known_at"], "sweep")
    asia = _span(_bars(market, _at(market, ASIA_LIQUIDITY[0], -1), _at(market, ASIA_LIQUIDITY[1]), 60), known_at=_at(market, ASIA_LIQUIDITY[1]))
    if asia is not None:
        add("asia_low", "long", asia["low"], asia["known_at"], "sweep")
        add("asia_high", "short", asia["high"], asia["known_at"], "sweep")
    overnight = _span(_bars(market, _at(market, "18:00", -1), _at(market, "09:00"), 60), known_at=_at(market, "09:00"))
    if overnight is not None:
        add("onl", "long", overnight["low"], overnight["known_at"], "sweep")
        add("onh", "short", overnight["high"], overnight["known_at"], "sweep")
    for index, span in enumerate(prior_sessions(market, 3), start=1):
        add(f"d{index}_low", "long", span["low"], span["known_at"], "sweep")
        add(f"d{index}_high", "short", span["high"], span["known_at"], "sweep")
    try:
        prior_rth = (market.prior("day") or {}).get("range")
    except Exception:
        prior_rth = None
    if prior_rth and prior_rth.get("low") is not None:
        add("prth_low", "long", _d(prior_rth["low"]), int(prior_rth.get("known_at") or market.start), "sweep")
        add("prth_high", "short", _d(prior_rth["high"]), int(prior_rth.get("known_at") or market.start), "sweep")
    value = prior_value_area(market)
    if value:
        known = int(value.get("known_at") or market.start)
        add("prth_val", "long", value.get("val"), known, "objective")
        add("prth_vah", "short", value.get("vah"), known, "objective")
        add("prth_poc", "both", value.get("poc"), known, "objective")
    if evrange:
        known = _at(market, "09:00")
        add("evrange_lower", "long", _d(evrange.get("lower")), known, "marker")
        add("evrange_upper", "short", _d(evrange.get("upper")), known, "marker")
        add("evrange_plus_50", "short", _d(evrange.get("plus_50")), known, "objective")
    for zone in pzones or []:
        side = zone.get("side") or ("long" if box is None or _d(zone["high"]) < box["eq"] else "short")
        near = _d(zone["high"]) if side == "long" else _d(zone["low"])
        add(f"pzone_{zone.get('tier', zone.get('anchor', '09:00'))}_{'lo' if side == 'long' else 'hi'}", side, near, _at(market, zone.get("anchor", "09:00")), "marker")
    return out


def _outside_reads(market, prior_day: Mapping[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """The news week (TBR pp.22-24) and NQ against ES overnight (TBR p.12), both
    known at the 09:00 read; unavailable, never guessed, when their data is not on disk."""
    from .jumbo_context import news_week, sister_index

    data_root = getattr(market, "data_root", None)
    news = news_week(_as_day(market), data_root)
    night = (_at(market, "18:00", -1), _at(market, "09:00"))
    overnight = _span(_bars(market, night[0], night[1], 60), known_at=night[1])
    span = None if not prior_day else prior_day.get("window")
    window = None if span is None else ((int(span.start), int(span.end)) if hasattr(span, "start") else tuple(int(x) for x in span))
    sister = sister_index(data_root=data_root, prior_window=window, overnight=night, nq_prior=prior_day, nq_overnight=overnight)
    return news, sister


def session_context(market) -> dict[str, Any]:
    """Everything the author reads before the open, plus the day's classification."""
    cached = getattr(market, "_jj_context", None)
    if cached is not None:
        return cached
    box = box_geometry(market, "ny")
    prior = prior_sessions(market, 3)
    value = prior_value_area(market)
    close_rows = _bars(market, _at(market, "08:59"), _at(market, "09:00"), 60)
    price_at_nine = _d(close_rows[-1].get("C")) if close_rows else (None if box is None else box["range_close"])
    open_rows = _bars(market, _at(market, "09:30"), _at(market, "09:31"), 60)
    rth_open = _d(open_rows[0].get("O")) if open_rows else None
    prior_day = prior[0] if prior else None
    size = range_class(None if box is None else box["width"], price_at_nine)
    purge = _purge_state(market, prior_day)
    day_text = str(_as_day(market))
    evrange = EVRANGE_FIXTURES.get(day_text)
    evrange_source = "author_printed_fixture" if evrange else None
    if evrange is None:
        evrange = generated_evrange(market, price_at_nine)
        evrange_source = None if evrange is None else "fitted_percentile_recipe"
    pzones = [dict(zone, source="author_printed_fixture") for zone in (PZONE_FIXTURES.get(day_text) or [])]
    pzone_source = "author_printed_fixture" if pzones else None
    if not pzones:
        pzones = generated_pzones(market, price_at_nine)
        pzone_source = "fitted_percentile_recipe" if pzones else None
    context = {
        "box": box,
        "prior_sessions": [{k: v for k, v in span.items() if k != "window"} for span in prior],
        "prior_value": value,
        "rth_open": rth_open,
        "price_at_0900": price_at_nine,
        "range_class": size,
        "open_location": _open_location(price_at_nine, prior_day, value),
        "rth_open_location": _open_location(rth_open, prior_day, value),
        "purge": purge,
        "evrange": evrange,
        "evrange_source": evrange_source,
        "pzones": pzones,
        "pzone_source": pzone_source,
        "sessionstat": sessionstat_envelope(market),
    }
    context["levels"] = drawn_levels(market, box, evrange=evrange, pzones=pzones)
    context["news_week"], context["sister_index"] = _outside_reads(market, prior_day)
    context["case"] = None
    context["read"] = session_read(market, context)
    context["case"] = context["read"]["classification"]
    setattr(market, "_jj_context", context)
    return context


# The play changes with the day (owner instruction 2026-09-17). Each branch is
# one play; every play is available every day and the day read names the
# PRIMARY one, which the selection takes first.
PLAY_OF_BRANCH = {
    "judas_reversal": "double_break",
    "judas_outbound": "single_break",
    "extension_reaction": "double_break",
    "single_extended": "single_break",
    "single_purged": "single_break",
    "internal_rotation": "big_range_eq",
    "other_session": "london",
    "timed_pzone_reversal": "pzone",
}
DOUBLE_BREAK_MAX_PCT = Decimal("1.2")
BIG_RANGE_MIN_PCT = Decimal("0.8")
OUTSIDE_VALUE = {"below_pdl", "below_val", "above_vah", "above_pdh"}


def _aligned(location, purge) -> bool:
    """The open sits outside prior value on the side the overnight already
    purged (JR p.34, 2026-07-28: "RTH open location in relation to previous day
    value/range and the current day 6-9")."""
    return (location in {"above_vah", "above_pdh"} and purge.get("purged_high") is True) or (
        location in {"below_val", "below_pdl"} and purge.get("purged_low") is True
    )


def _plays_for(location, pct, purge, *, pzone: bool) -> tuple[str, list[str]]:
    """The day's classification.

    The author's rule, in his words (2026-07-28, JR p.34): "RTH open location in
    relation to previous day value/range and the current day 6-9 ... Discard
    mean reversion and range double breaks when these things align" -- an open
    outside prior value on the side the overnight already purged is the single
    break (trend) day. His 2026-06-08 table by range size (3,249 days) adds the
    size rule: above 1.2% of price the single break leads; below it the double
    break leads.
    """
    aligned = _aligned(location, purge)
    plays = ["london", "double_break", "single_break", "big_range_eq", "pzone"]
    if pct is None or location is None:
        return "unknown", plays
    # The 2026-06-08 table by range size decides first: up to 0.5% of price the
    # double break leads by a wide margin (55.5 and 48.1 against 20-26 for
    # either single break) and the alignment does not overturn it (2025-10-03,
    # 2026-01-02, 2026-09-01 open outside value on the purged side and are
    # Judas days); at 1.2% and above the single break leads. Between, the two
    # are level in his table and the alignment rule decides.
    if pct >= DOUBLE_BREAK_MAX_PCT:
        return "single_break", plays
    if pct < Decimal("0.5"):
        return "double_break", plays
    return ("single_break" if aligned else "double_break"), plays


def session_read(market, context: Mapping[str, Any]) -> dict[str, Any]:
    """The day's read on the two clocks (09:00 and the RTH open), and the plays."""
    size = context.get("range_class") or {}
    pct = size.get("pct")
    purge = context.get("purge") or {}
    pre_location = context.get("open_location")
    post_location = context.get("rth_open_location") or pre_location
    pre_class, plays = _plays_for(pre_location, pct, purge, pzone=True)
    post_class, _ = _plays_for(post_location, pct, purge, pzone=True)
    unswept = [row["kind"] for row in context.get("levels") or [] if row["kind"] in {"asia_high", "asia_low", "london_high", "london_low", "onh", "onl"}]
    if post_class == "single_break":
        primary = "single_break"
    elif post_class == "double_break":
        primary = "double_break"
    else:
        primary = None
    big_range = pct is not None and pct >= BIG_RANGE_MIN_PCT
    inside_value = post_location == "inside_value"
    aligned = _aligned(post_location, purge) or _aligned(pre_location, purge)
    direction = None
    if post_class == "single_break":
        if purge.get("purged_low") is True and purge.get("purged_high") is not True:
            direction = "short"
        elif purge.get("purged_high") is True and purge.get("purged_low") is not True:
            direction = "long"
        elif post_location in {"below_val", "below_pdl"}:
            direction = "short"
        elif post_location in {"above_vah", "above_pdh"}:
            direction = "long"
    return {
        "classification": post_class,
        "classification_pre_open": pre_class,
        "plays": sorted(plays),
        "plays_pre_open": sorted(plays),
        "plays_post_open": sorted(plays),
        "primary_play": primary,
        "trend_direction": direction,
        "big_range": big_range,
        "aligned": aligned,
        "open_inside_value": inside_value,
        "inputs": {
            "range_pct": pct,
            "range_bin": size.get("bin"),
            "open_location": pre_location,
            "rth_open_location": post_location,
            "overnight_purged_high": purge.get("purged_high"),
            "overnight_purged_low": purge.get("purged_low"),
            "overnight_balanced": None if not purge.get("available") else not (purge.get("purged_high") or purge.get("purged_low")),
            "edges_still_drawn": unswept,
            "prior_value": None if not context.get("prior_value") else {
                "vah": context["prior_value"].get("vah"),
                "val": context["prior_value"].get("val"),
                "poc": context["prior_value"].get("poc"),
            },
            "evrange_source": context.get("evrange_source"),
            "pzone_source": context.get("pzone_source"),
        },
        "news_week": context.get("news_week"),
        "sister_index": context.get("sister_index"),
        "unavailable_inputs": [name for name, body in (("sister_index_relative_strength", context.get("sister_index")), ("news_calendar", context.get("news_week"))) if not (body or {}).get("available")],
        "read_inputs_missing": [
            name
            for name, present in (
                ("range_pct", pct is not None),
                ("open_location", pre_location is not None),
                ("rth_open_location", post_location is not None),
                ("prior_value_area", bool(context.get("prior_value")) and context["prior_value"].get("val") is not None),
                ("overnight_purge", bool(purge.get("available"))),
            )
            if not present
        ],
        "prior_value_unavailable_reason": (context.get("prior_value") or {}).get("unavailable"),
        "rule": "single break when the open sits outside prior value on the side the overnight already purged (JR p.34, 2026-07-28) or the 6-9 range exceeds 1.2% of price (the 2026-06-08 table); otherwise the double-break / Judas day; the EQ play in addition on a big range (>=0.8%) or an open inside prior value; London and the P-zones run on their own clocks",
    }


def _purge_state(market, prior_day: Mapping[str, Any] | None) -> dict[str, Any]:
    """Which prior-day liquidity was already taken before 09:00."""
    overnight = _span(_bars(market, _at(market, "18:00", -1), _at(market, "09:00"), 60), known_at=_at(market, "09:00"))
    if overnight is None or not prior_day:
        return {"available": False, "purged_high": None, "purged_low": None}
    pdh, pdl = _d(prior_day.get("high")), _d(prior_day.get("low"))
    return {
        "available": True,
        "purged_high": None if pdh is None else overnight["high"] > pdh,
        "purged_low": None if pdl is None else overnight["low"] < pdl,
        "overnight_high": overnight["high"],
        "overnight_low": overnight["low"],
        "overnight_width": overnight["high"] - overnight["low"],
    }



SESSIONSTAT_SAMPLE = 60


_EXCURSION_CACHE: dict[tuple, tuple[Decimal, Decimal] | None] = {}


def _session_excursion(market, span: Mapping[str, Any], window: tuple[str, str]) -> tuple[Decimal, Decimal] | None:
    """High and low excursion of one past session's clock window from its open."""
    key = (market.instrument_id, span["date"], window)
    if key in _EXCURSION_CACHE:
        return _EXCURSION_CACHE[key]
    win = span.get("window")
    result = None
    if win is not None:
        day = date.fromisoformat(span["date"])
        try:
            rows = win.bars(clock(day, window[0]), clock(day, window[1]), 300)
        except Exception:
            rows = []
        opening = _d(rows[0].get("O")) if rows else None
        if rows and opening is not None:
            hi = max(_d(r["H"]) for r in rows if r.get("H") is not None)
            lo = min(_d(r["L"]) for r in rows if r.get("L") is not None)
            result = (hi - opening, opening - lo)
    _EXCURSION_CACHE[key] = result
    return result


def minimum_average(highs: Sequence[Decimal], lows: Sequence[Decimal]) -> Decimal:
    """SessionStat's "Minimum Average": the mean, over the sample, of each session's smaller excursion."""
    return sum(min(h, l) for h, l in zip(highs, lows)) / Decimal(len(highs))


def sessionstat_envelope(market, window: tuple[str, str] = ("09:00", "12:00")) -> dict[str, Any] | None:
    """J13: the SessionStat envelope, computed rather than treated as injected.

    SessionStat+ defines it as the mean and median high/low excursion of the
    selected clock from that session's open over the last 60 sessions, with 0.5
    expansions and a "minimum average" level. Three printed readouts calibrate
    it (2025-05-23 4-hour Exp 74.53 / Dist 65.55 / Min 40.74; 2025-09-09 RTH
    75.28 / 100.8 / 37.14; 2026-07-06 the 09:00-12:00 boxes).

    Sixty prior windows are sixty cached-window reads, so the envelope is
    computed when the caller asks for it (``market.jj_sessionstat`` truthy,
    the default for a full-history run where consecutive dates share the cache)
    and skipped for a scattered-date replay, where it only ever decorates an
    operand and never gates an entry.
    """
    injected = getattr(market, "sessionstat_box", None)
    if injected:
        return dict(injected)
    if not getattr(market, "jj_sessionstat", False) or _as_day(market) is None:
        return None
    cache_key = f"_jj_sessionstat_{window[0]}_{window[1]}"
    cached = getattr(market, cache_key, "missing")
    if cached != "missing":
        return cached
    highs: list[Decimal] = []
    lows: list[Decimal] = []
    for span in prior_sessions(market, SESSIONSTAT_SAMPLE):
        excursion = _session_excursion(market, span, window)
        if excursion is None:
            continue
        highs.append(excursion[0])
        lows.append(excursion[1])
    if len(highs) < 10:
        setattr(market, cache_key, None)
        return None

    def _mean(values: list[Decimal]) -> Decimal:
        return sum(values) / Decimal(len(values))

    def _median(values: list[Decimal]) -> Decimal:
        ordered = sorted(values)
        mid = len(ordered) // 2
        return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2

    result = {
        "window": list(window),
        "sample": len(highs),
        "high_mean": _mean(highs),
        "high_median": _median(highs),
        "low_mean": _mean(lows),
        "low_median": _median(lows),
        # "It's the minimum average range if the 9-12 session" (JR p.68). His three printed tables put it
        # well under BOTH side averages (40.74 against 74.53 / 65.55; 67.25 against 140.66 / 118.95; about
        # 37.1 against 75.3 / 100.8), which the smaller of the two means can never be: it is the mean of
        # each session's SMALLER excursion, the swing "that falls short from highs and lows" (SS p.3)
        "minimum_average": minimum_average(highs, lows),
        "expansion_0_5_high": _mean(highs) * Decimal("1.5"),
        "expansion_0_5_low": _mean(lows) * Decimal("1.5"),
    }
    setattr(market, cache_key, result)
    return result


# ---------------------------------------------------------------------------
# confirmation signatures (audit 1.2: faithful, kept unchanged)


def _signature_stop(side: str, band_lo: Decimal, band_hi: Decimal) -> Decimal:
    """The stop of an orderblock or rejection-block fill: a tick beyond the
    block's extreme, or its midpoint under the aggressive placement."""
    if SIGNATURE_STOP == "aggressive":
        return (band_lo + band_hi) / 2
    if SIGNATURE_STOP != "conservative":
        raise ValueError(f"SIGNATURE_STOP must be conservative or aggressive, not {SIGNATURE_STOP!r}")
    return (band_lo - TICK) if side == "long" else (band_hi + TICK)


def _three_candle_ob(bars: list[dict[str, Any]], side: str, level: Decimal | None = None) -> dict[str, Any] | None:
    """TBR pp.27-28: C2 sweeps C1; C3 closes beyond C2's opposite extreme."""
    rows = [row for row in bars if row.get("C") is not None and row.get("H") is not None and row.get("L") is not None]
    for first, second, third in zip(rows, rows[1:], rows[2:]):
        if not (first["end"] <= second["start"] and second["end"] <= third["start"]):
            continue
        f_l, f_h = _d(first["L"]), _d(first["H"])
        s_l, s_h, s_c = _d(second["L"]), _d(second["H"]), _d(second["C"])
        t_c = _d(third["C"])
        if level is not None and not (s_l <= level <= s_h):
            continue
        stop = _signature_stop(side, s_l, s_h)
        if side == "long":
            swept, closed = s_l < f_l, t_c > s_h
        else:
            swept, closed = s_h > f_h, t_c < s_l
        if swept and closed:
            return {
                "ok": True,
                "kind": "orderblock",
                "at": int(third["known_at"]),
                "entry": t_c,
                "signal_close": s_c,
                "signal_at": int(second["known_at"]),
                "stop": stop,
                "band": [s_l, s_h],
            }
    return None


def _rejection_block(bars: list[dict[str, Any]], side: str, level: Decimal | None = None) -> dict[str, Any] | None:
    """TBR p.29: a rejection wick at the level; the next candle closes beyond it."""
    rows = [
        row
        for row in bars
        if row.get("O") is not None and row.get("C") is not None and row.get("H") is not None and row.get("L") is not None
    ]
    for sweep, close in zip(rows, rows[1:]):
        if sweep["end"] > close["start"]:
            continue
        s_o, s_c, s_h, s_l = _d(sweep["O"]), _d(sweep["C"]), _d(sweep["H"]), _d(sweep["L"])
        c_c = _d(close["C"])
        if level is not None and not (s_l <= level <= s_h):
            continue
        body_lo, body_hi = min(s_o, s_c), max(s_o, s_c)
        body = body_hi - body_lo
        if side == "long":
            wick, closed, band = body_lo - s_l, c_c > s_h, [s_l, body_lo]
        else:
            wick, closed, band = s_h - body_hi, c_c < s_l, [body_hi, s_h]
        stop = _signature_stop(side, band[0], band[1])
        if wick > body and closed:
            return {
                "ok": True,
                "kind": "rejection_block",
                "at": int(close["known_at"]),
                "entry": c_c,
                "signal_close": s_c,
                "signal_at": int(sweep["known_at"]),
                "stop": stop,
                "band": band,
            }
    return None


def _absorption(bar: Mapping[str, Any], avg_volume: Decimal | None) -> bool | None:
    """Absorption Zone+: body <= 0.6 of range, volume >= 1.5x the 14-period average."""
    open_, high, low, close = _d(bar.get("O")), _d(bar.get("H")), _d(bar.get("L")), _d(bar.get("C"))
    if None in (open_, high, low, close):
        return None
    span = high - low
    if span <= 0:
        span = TICK
    body = abs(close - open_) / span
    if avg_volume is None:
        return None  # no fourteen bars to measure against: the read is unknown, never a pass
    return body <= Decimal("0.6") and _d(bar.get("V") or bar.get("volume") or 0) >= Decimal("1.5") * avg_volume


def _avg_volume(market, before_ns: int, seconds: int = 60, n: int = 14) -> Decimal | None:
    rows = _bars(market, int(before_ns) - n * seconds * 1_000_000_000, int(before_ns), seconds)
    if len(rows) < n:
        return None
    window = rows[-n:]
    return sum(_d(row.get("V") or row.get("volume") or 0) for row in window) / Decimal(n)


def confirm_pack(market, start_ns: int, side: str, level: Decimal | None, end_ns: int) -> dict[str, Any]:
    """F11/J7/J-B: the rejection block or orderblock at the level.

    TBR pp.27-29 names 2-, 3- and 5-minute candles. The author's fills sit two
    to six minutes after the touch (2025-09-09 10:35, 2025-10-13 09:05,
    2026-01-02 09:22, 2025-10-06 03:40), which is the two-minute reading: the
    rejection block is "the close of the next candle beyond the sweep candle",
    two candles, six minutes at worst on the three-minute clock. The faster
    clock is therefore searched first and the slower ones are kept as
    alternative fills of the same opportunity.
    """
    pack: dict[str, Any] = {"ob_2m": None, "ob_3m": None, "ob_5m": None, "rejection_block": None, "absorption": None}
    best: dict[str, Any] | None = None
    seen = False
    for seconds, key in ((120, "ob_2m"), (180, "ob_3m"), (300, "ob_5m")):
        rows = _bars(market, int(start_ns), int(end_ns), seconds)
        complete = [row for row in rows if row.get("C") is not None]
        found_here: dict[str, Any] | None = None
        if len(complete) >= 2:
            seen = True
            found_rb = _rejection_block(rows, side, level=level)
            if found_rb is not None:
                pack["rejection_block"] = True
                found_here = found_rb
            elif pack["rejection_block"] is None:
                pack["rejection_block"] = False
        if len(complete) >= 3:
            seen = True
            found_ob = _three_candle_ob(rows, side, level=level)
            pack[key] = found_ob is not None
            if found_ob is not None and (found_here is None or found_ob["at"] < found_here["at"]):
                found_here = found_ob
        if found_here is not None and best is None:
            best = found_here
            best["timeframe_seconds"] = seconds
    minute_rows = _bars(market, int(start_ns), int(end_ns), 60)
    for row in minute_rows:
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if level is not None and (lo is None or hi is None or not (lo <= level <= hi)):
            continue
        verdict = _absorption(row, _avg_volume(market, int(row["start"])))
        if verdict:
            pack["absorption"] = True
            if best is None:
                best = {
                    "ok": True,
                    "kind": "absorption",
                    "at": int(row["known_at"]),
                    "entry": _d(row.get("C")),
                    "stop": (lo - TICK) if side == "long" else (hi + TICK),
                    "band": [lo, hi],
                    "timeframe_seconds": 60,
                }
            break
    if pack["absorption"] is None and minute_rows:
        pack["absorption"] = False
    pack["confirmed"] = best
    pack["verdict"] = "pass" if best is not None else ("fail" if seen else "unknown")
    return pack


# ---------------------------------------------------------------------------
# sweeps and contacts


def sweep_cycles(market, *, level: Decimal, side: str, begin: int, end: int, max_cycles: int = 2) -> list[dict[str, Any]]:
    """Sweeps of a drawn level inside the action window, on one-minute bars."""
    rows = _bars(market, begin, end, 60)
    cycles: list[dict[str, Any]] = []
    index = 0
    # A sweep is a raid THROUGH the line from the entry side: the bar before it
    # closes on the entry side of the line (above it for a long, below it for
    # a short) or the sweep bar opens there. A bar that merely sits beyond the
    # line because price was already there is not a sweep (coordinator rebuild
    # 2026-09-17: without this a breakdown from above counted as a "short
    # failure" of the box low).
    while index < len(rows) and len(cycles) < max_cycles:
        row = rows[index]
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None:
            index += 1
            continue
        if not (lo < level if side == "long" else hi > level):
            index += 1
            continue
        prior_close = _d(rows[index - 1].get("C")) if index > 0 else None
        opened = _d(row.get("O"))
        entry_side = (prior_close is not None and ((prior_close >= level) if side == "long" else (prior_close <= level))) or (
            opened is not None and ((opened >= level) if side == "long" else (opened <= level))
        )
        if not entry_side:
            index += 1
            continue
        start = int(row["start"])
        extreme = lo if side == "long" else hi
        reclaim = None
        cursor = index
        while cursor < len(rows):
            item = rows[cursor]
            i_lo, i_hi, i_c = _d(item.get("L")), _d(item.get("H")), _d(item.get("C"))
            if side == "long" and i_lo is not None and i_lo < extreme:
                extreme = i_lo
            if side == "short" and i_hi is not None and i_hi > extreme:
                extreme = i_hi
            if i_c is not None and ((i_c >= level) if side == "long" else (i_c <= level)):
                reclaim = item
                break
            cursor += 1
        cycles.append(
            {
                "cycle": len(cycles),
                "sweep": row,
                "sweep_at": start,
                "extreme": extreme,
                "reclaim": reclaim,
                "reclaim_at": None if reclaim is None else int(reclaim["known_at"]),
            }
        )
        index = cursor + 1 if reclaim is not None else len(rows)
    return cycles


# two tests of a line per session (2026-06-05 buys R-Lo at 05:03 after two
# earlier round trips); the scan's only cap: both call sites read it at call
# time so a rescan override reaches them (the literal 2 they carried made the
# 2026-09-17 contacts candidates inert)
MAX_CONTACTS_PER_LEVEL = 2


def first_touch(market, *, level: Decimal, begin: int, end: int) -> dict[str, Any] | None:
    for row in _bars(market, begin, end, 60):
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is not None and hi is not None and lo <= level <= hi:
            return row
    return None


def level_contacts(
    market,
    *,
    level: Decimal,
    begin: int,
    end: int,
    departure: Decimal,
    max_contacts: int | None = None,
) -> list[dict[str, Any]]:
    """Each distinct test of a level, not only the first.

    The author trades a level whenever it is tested: 2025-10-07 buys the London
    quadrant at 04:30 after the session had already traded through it, and
    2026-06-05 buys R-Lo at 05:03 after two earlier round trips. A re-touch
    counts once price has left the level by ``departure``.
    """
    if max_contacts is None:
        max_contacts = MAX_CONTACTS_PER_LEVEL  # read at call time so a rescan override reaches it
    out: list[dict[str, Any]] = []
    ready = True
    for row in _bars(market, begin, end, 60):
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None:
            continue
        if lo <= level <= hi:
            if ready:
                out.append(row)
                ready = False
                if len(out) >= max_contacts:
                    break
        elif lo > level + departure or hi < level - departure:
            ready = True
    return out


def depth_class(depth: Decimal | None, width: Decimal | None) -> str | None:
    """J5: how far beyond the edge the sweep ran, in units of the range width."""
    if depth is None or width is None or width <= 0:
        return None
    ratio = depth / width
    if ratio < MEAN_REVERSAL[0]:
        return DEPTH_CLASSES[0]
    if ratio <= MEAN_REVERSAL[1]:
        return DEPTH_CLASSES[1]
    return DEPTH_CLASSES[2]


def exhaustion_hit(context: Mapping[str, Any], price: Decimal | None, side: str, *, exclude_kind: str | None = None) -> dict[str, Any]:
    """Did the sweep reach the exhaustion area the author fades from?

    The area is the 0.33-0.66 mean-reversal band and everything beyond it, the
    0.5 projection, or another drawn level (an overnight/London/Asia extreme, a
    prior-day extreme, an EVRange line or a printed P-zone). 2026-02-24 ran to
    -0.94W and 2025-01-28 to -0.65W: past the band is still exhaustion, short of
    it is not.

    The band is measured from the box edges, so the test applies to a swept box
    edge. Any other drawn level is itself the location the author marked.
    """
    box = context.get("box")
    hits: list[str] = []
    if price is None or box is None:
        return {"in_band": None, "at_half": None, "coincident": [], "reached": None, "at_or_beyond_band": None}
    band = box["mean_reversal"]["lower" if side == "long" else "upper"]
    in_band = band[0] <= price <= band[1]
    near = band[1] if side == "long" else band[0]
    at_or_beyond = price <= near if side == "long" else price >= near
    half = box["ladder"]["minus_0.5" if side == "long" else "plus_0.5"]
    at_half = abs(price - half) <= LEVEL_COINCIDENCE
    for row in context.get("levels") or []:
        if row["kind"] == exclude_kind:
            continue  # a shallow poke may not "coincide" with the level it swept
        if abs(row["price"] - price) <= LEVEL_COINCIDENCE:
            hits.append(row["kind"])
    ev = context.get("evrange") or {}
    for key in ("lower", "upper", "plus_50"):
        value = ev.get(key)
        if value is not None and abs(value - price) <= LEVEL_COINCIDENCE:
            hits.append(f"evrange_{key}")
    for zone in context.get("pzones") or []:
        low, high = zone["low"], zone["high"]
        if low - LEVEL_COINCIDENCE <= price <= high + LEVEL_COINCIDENCE:
            hits.append(f"pzone_{zone.get('anchor', '09:00')}")
    box_edge = exclude_kind in {"box_low", "box_high"}
    reached = bool(at_or_beyond or at_half or hits) if box_edge else True
    return {
        "in_band": in_band,
        "at_or_beyond_band": at_or_beyond,
        "at_half": at_half,
        "coincident": hits,
        "level_is_box_edge": box_edge,
        "reached": reached,
    }


def objective_ladder(box: Mapping[str, Any], side: str) -> list[dict[str, Any]]:
    """J1: EQ -> range open -> opposite edge -> +/-0.5 -> the extension band.

    The author's own retrace table (2026-01-02, 2,043 sweeps) prints EQ 92.8%,
    range open 86.8%, opposite edge 66.2% for the 09:00-10:00 segment; his exits
    scale along exactly this ladder. The first rung is EQ, never "plus_0_5".
    """
    rungs = [
        {"name": "eq", "price": box["eq"]},
        {"name": "range_open", "price": box["range_open"]},
        {"name": "opposite_edge", "price": box["high"] if side == "long" else box["low"]},
        {"name": "half_projection", "price": box["ladder"]["plus_0.5" if side == "long" else "minus_0.5"]},
        {
            "name": "extension_band",
            "price": box["ladder"]["plus_1.33" if side == "long" else "minus_1.33"],
        },
    ]
    # The author's order is the order of his own retrace table, not the order
    # of the prices: EQ 92.8%, range open 86.8%, opposite edge 66.2%, then the
    # half projection and the extension band. Which rung is nearest depends on
    # where the range opened; the caller filters by direction.
    return [row for row in rungs if row["price"] is not None]


# ---------------------------------------------------------------------------
# episode assembly


def _stage(name: str, verdict: str, at_ns: int | None, **operands: Any) -> dict[str, Any]:
    return {"stage": name, "verdict": verdict, "at_ns": at_ns, "operands": jsonable(operands)}


def _gate(stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocked = None
    blocker = None
    out: list[dict[str, Any]] = []
    by_name = {row["stage"]: row for row in stages}
    for name in STAGE_ORDER:
        row = by_name.get(name)
        if row is None:
            continue
        if blocked and row.get("verdict") == "pass":
            operands = dict(row.get("operands") or {})
            operands["blocked_by"] = blocker
            row = {**row, "verdict": "fail", "operands": operands}
        out.append(row)
        if not blocked and row.get("verdict") == "fail":
            blocked, blocker = True, name
    return out


def _verdict(stages: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    failed = [row["stage"] for row in stages if row["verdict"] == "fail"]
    unknown = [row["stage"] for row in stages if row["verdict"] == "unknown"]
    if unknown and not failed:
        return "unknown", failed, unknown
    if failed:
        return "fail", failed, unknown
    return "pass", failed, unknown


def _episode(
    market,
    *,
    branch: str,
    side: str,
    stages: list[dict[str, Any]],
    decision_at: int | None,
    entry: Decimal | None,
    stop: Decimal | None,
    target: Decimal | None,
    reference: Mapping[str, Any] | None,
    trigger: Mapping[str, Any] | None,
    values: dict[str, Any],
    geometry: dict[str, Any],
) -> dict[str, Any]:
    ordered = _gate(stages)
    verdict, failed, unknown = _verdict(ordered)
    if decision_at is None:
        decision_at = int(market.end)
        if verdict == "pass":
            verdict, unknown = "unknown", list(unknown) + ["decision_at"]
    # An entry may never be filled before the evidence that admitted it. The
    # decision time is the latest at_ns of every stage on the episode; an entry
    # priced earlier than that is a causality failure, reported as one.
    stamps = [int(row["at_ns"]) for row in ordered if row.get("at_ns") is not None]
    evidence_at = max(stamps) if stamps else None
    causal = evidence_at is None or int(decision_at) >= evidence_at
    if not causal:
        verdict = "fail"
        failed = list(failed) + ["causality"]
        ordered = ordered + [
            {
                "stage": "confirmation",
                "verdict": "fail",
                "at_ns": evidence_at,
                "operands": {"reason": "entry_precedes_evidence", "decision_at": int(decision_at), "evidence_at": evidence_at},
            }
        ]
    status = {"pass": "setup", "fail": "no_setup", "unknown": "data_unavailable"}[verdict]
    identity = {
        "method": FAMILY,
        "branch": branch,
        "side": side,
        "session_date": str(_as_day(market)),
        "instrument_id": market.instrument_id,
        "reference_id": None if reference is None else reference.get("id"),
        "occurrence_at": None if trigger is None else trigger.get("start"),
        "level": str(values.get("reference_px")),
        "cycle": values.get("cycle"),
        "baseline": B02_VERSION,
    }
    stop_points = None if entry is None or stop is None else abs(entry - stop)
    geometry = dict(geometry)
    geometry.update(
        {
            "entry": entry,
            "stop": stop,
            "target": target,
            "reference_level": values.get("reference_px"),
            "stop_points": stop_points,
            "reward_points": None if entry is None or target is None else abs(target - entry),
            "r_multiple_at_target": None
            if entry is None or target is None or not stop_points
            else abs(target - entry) / stop_points,
        }
    )
    values = dict(values)
    values.update(
        {
            "branch": branch,
            "side": side,
            "decision_at": decision_at,
            "evidence_at": evidence_at,
            "confirmation_delay_ns": None if evidence_at is None else int(decision_at) - evidence_at,
        }
    )
    return jsonable(
        {
            "schema": "phase1-historical-episode-v2",
            "candidate_id": "b03:" + content_hash(identity)[:32],
            "method": FAMILY,
            "branch": branch,
            "predicate": "sequence",
            "side": side,
            "session_date": str(_as_day(market)),
            "instrument_id": market.instrument_id,
            "reference_id": identity["reference_id"],
            "trigger_id": None if trigger is None else trigger.get("bar_id"),
            "occurrence_at": identity["occurrence_at"],
            "decision_at": decision_at,
            "values": values,
            "stages": ordered,
            "rules": rules_payload(),
            "research_verdict": verdict,
            "failed": failed,
            "unknown": unknown,
            "strategy_assessment": {"status": status, "baseline_version": B02_VERSION},
            "reference": None if reference is None else {k: v for k, v in reference.items() if k != "window"},
            "trigger": trigger,
            "geometry": geometry,
            "baseline_version": B02_VERSION,
        }
    )


def _document(market, branch: str, episodes: list[dict[str, Any]], omissions: list[dict[str, Any]], selection=None, day_read=None) -> dict[str, Any]:
    counts = {"pass": 0, "fail": 0, "unknown": 0}
    for episode in episodes:
        counts[episode["research_verdict"]] += 1
    day = _as_day(market) if market is not None else None
    return jsonable(
        {
            "schema_version": "research-family-b02-scan-v1",
            "baseline_version": B02_VERSION,
            "method_id": FAMILY,
            "family": FAMILY,
            "branch": branch,
            "session_date": None if day is None else day.isoformat(),
            "clock_zone": "America/New_York",
            "chart_clock_notes": {"ninjatrader_2026": "UK local", "ticket_2025-01-28": "UTC", "source_prose": "ET"},
            "episodes": episodes,
            "omissions": omissions,
            "rules": rules_payload(),
            "N_observed": len(episodes),
            "n": counts["pass"] + counts["fail"],
            "p": counts["pass"],
            "f": counts["fail"],
            "u": counts["unknown"],
            "selection": selection,
            "day_read": day_read,
            "populations": {
                "B0.2": {
                    "episodes": len(episodes),
                    "setup": counts["pass"],
                    "rejected": counts["fail"],
                    "unknown": counts["unknown"],
                    "no_setup": counts["fail"],
                }
            },
        }
    )


def _context_stage(context: Mapping[str, Any], at_ns: int, **extra: Any) -> dict[str, Any]:
    size = context.get("range_class") or {}
    purge = context.get("purge") or {}
    return _stage(
        "context",
        extra.pop("verdict", "pass"),
        at_ns,
        case=context.get("case"),
        range_pct=size.get("pct"),
        range_bin=size.get("bin"),
        open_location=context.get("open_location"),
        rth_open_location=context.get("rth_open_location"),
        purged_high=purge.get("purged_high"),
        purged_low=purge.get("purged_low"),
        **extra,
    )


# ---------------------------------------------------------------------------
# branches



def _scan_extension_reaction(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """After 10:00, a touch of the 1.33-1.66 band beyond an edge with a
    rejection signature; reverse toward the range."""
    context = session_context(market)
    box = context.get("box")
    if box is None:
        return _value_layer_episodes(market, context, "extension_reaction"), []
    bands = box["extension"]
    if not bands.get("available"):
        return _value_layer_episodes(market, context, "extension_reaction"), [{"reason": "extension_band_unavailable", "branch": "extension_reaction"}]
    begin, end = _at(market, NY_EXTENSION_ACTION[0]), _at(market, NY_EXTENSION_ACTION[1])
    stat = context.get("sessionstat")
    episodes = []
    for side, band, target in (
        ("short", bands["upper"], box["high"]),
        ("long", bands["lower"], box["low"]),
    ):
        touch = None
        for row in _bars(market, begin, end, 60):
            lo, hi = _d(row.get("L")), _d(row.get("H"))
            if lo is None or hi is None:
                continue
            if lo <= band[1] and hi >= band[0]:
                touch = row
                break
        level = band[0] if side == "short" else band[1]
        pack = (
            confirm_pack(market, int(touch["end"]), side, None, min(end, int(touch["end"]) + 10 * NS_MINUTE))
            if touch is not None
            else {"verdict": "fail", "confirmed": None, "ob_2m": None, "ob_3m": None, "ob_5m": None, "rejection_block": None, "absorption": None}
        )
        confirmed = pack.get("confirmed")
        entry = None if confirmed is None else confirmed["entry"]
        at_ns = None if confirmed is None else confirmed["at"]
        extreme = None
        if touch is not None:
            extreme = _d(touch.get("H")) if side == "short" else _d(touch.get("L"))
        stop = None if confirmed is None else confirmed["stop"]
        stat_hit = None
        if stat is not None and context.get("rth_open") is not None and extreme is not None:
            edge = context["rth_open"] + stat["high_mean"] if side == "short" else context["rth_open"] - stat["low_mean"]
            stat_hit = abs(edge - extreme) <= LEVEL_COINCIDENCE
        stages = [
            _context_stage(context, begin, branch="extension_reaction", after_1000=True),
            _stage("reference", "pass", box["known_at"], id=box["id"], band=[band[0], band[1]], width=box["width"]),
            _stage("location", "pass" if touch is not None else "fail", None if touch is None else int(touch["start"]), band=[band[0], band[1]], touched=touch is not None, sessionstat_coincident=stat_hit, reason=None if touch is not None else "band_not_reached_after_1000"),
            _stage("trigger", "pass" if touch is not None else "fail", None if touch is None else int(touch["start"]), extreme=extreme),
            _stage("confirmation", pack["verdict"], at_ns, ob_2m=pack["ob_2m"], ob_3m=pack["ob_3m"], ob_5m=pack["ob_5m"], rejection_block=pack["rejection_block"], absorption=pack["absorption"], kind=None if confirmed is None else confirmed["kind"]),
            _stage("risk", "pass" if entry is not None and stop is not None and sign(side) * (entry - stop) > 0 else "fail", at_ns, entry=entry, stop=stop),
            _stage("objective", "pass" if entry is not None and sign(side) * (target - entry) > 0 else "fail", at_ns, target=target, label="nearest range edge"),
            _stage("management", "pass", at_ns),
        ]
        episodes.append(
            _episode(
                market,
                branch="extension_reaction",
                side=side,
                stages=stages,
                decision_at=at_ns,
                entry=entry,
                stop=stop,
                target=target,
                reference=box,
                trigger=touch,
                values={"reference_px": level, "reference_kind": "extension_band", "cycle": 0, "confirmation_mode": None if confirmed is None else confirmed["kind"], "sessionstat_coincident": stat_hit},
                geometry={"band": [band[0], band[1]], "first_objective": target},
            )
        )
        if EXTENSION_BAND_LIMIT and touch is not None and extreme is not None:
            # the limit rests at the band's near line and, if the touching bar
            # reaches it, at the far line; filled at the touch, decided when
            # the touching bar closes, stop beyond the bar's extreme
            far = band[0] if side == "long" else band[1]
            near_line = band[1] if side == "long" else band[0]
            reached_far = (extreme <= far) if side == "long" else (extreme >= far)
            for label, line in (("band_near_limit", near_line), ("band_far_limit", far)):
                if label == "band_far_limit" and not reached_far:
                    continue
                touch_end = int(touch.get("known_at") or touch["end"])
                limit_stop = (extreme - STOP_BEYOND_EXTREME) if side == "long" else (extreme + STOP_BEYOND_EXTREME)
                limit_stages = [dict(s) for s in stages]
                for s in limit_stages:
                    if s["stage"] == "confirmation":
                        s.update(verdict="pass", at_ns=touch_end, operands={**(s.get("operands") or {}), "kind": label})
                    if s["stage"] in ("risk", "objective", "management"):
                        s.update(verdict="pass" if s["stage"] != "objective" or sign(side) * (target - line) > 0 else "fail", at_ns=touch_end)
                episodes.append(
                    _episode(
                        market,
                        branch="extension_reaction",
                        side=side,
                        stages=limit_stages,
                        decision_at=touch_end,
                        entry=line,
                        stop=limit_stop,
                        target=target,
                        reference=box,
                        trigger=touch,
                        values={"reference_px": line, "reference_kind": "extension_band", "cycle": 0, "confirmation_mode": label, "sessionstat_coincident": stat_hit},
                        geometry={"band": [band[0], band[1]], "first_objective": target},
                    )
                )
    episodes.extend(_value_layer_episodes(market, context, "extension_reaction"))
    return episodes, []


def _spike_turn(market, *, level: Decimal, side: str, bar: Mapping[str, Any], end: int) -> dict[str, Any] | None:
    """The tagging bar turns; the fill is the open of the bar after it.

    FITTED, shared with the Green Bird spike turn: the bar must reach beyond the
    level and close at least ``SPIKE_GIVE_BACK`` of its own range back from the
    extreme it made. Fitted on 2026-07-27 09:00 (gives back 12.6% ... see the
    rules table) and the two Green Bird tickets; not a source constant.
    """
    hi, lo, close = _d(bar.get("H")), _d(bar.get("L")), _d(bar.get("C"))
    if hi is None or lo is None or close is None:
        return None
    beyond = hi > level if side == "short" else lo < level
    if not beyond:
        return None
    span = hi - lo
    if span <= 0:
        return None
    give_back = (hi - close) if side == "short" else (close - lo)
    if give_back < span * SPIKE_GIVE_BACK:
        return None
    following = _bars(market, int(bar["end"]), min(int(end), int(bar["end"]) + 5 * NS_MINUTE), 60)
    if not following:
        return None
    entry = _d(following[0].get("O"))
    if entry is None:
        return None
    stop = (hi + STOP_BEYOND_EXTREME) if side == "short" else (lo - STOP_BEYOND_EXTREME)
    return {"entry": entry, "at": int(following[0].get("known_at") or following[0].get("end")), "stop": stop, "give_back": give_back / span}


def _two_minute_reclaim(market, *, level: Decimal, side: str, begin: int, end: int) -> dict[str, Any] | None:
    """The first two-minute candle that closes back through the line.

    The author's confirmation clock is the two-minute chart (audit 1.1,
    "Confirmation"). He reads a FIXED two-minute grid, so the candle is the grid
    bar that ends after the test -- not a bar re-anchored to the moment the
    level was touched. 2026-07-10: the 11:00 dip through the lower quadrant is
    confirmed by the 11:00-11:02 candle closing 29,810.75 (his 29,809).
    """
    grid_origin = _at(market, "09:00")
    step = 2 * NS_MINUTE
    first = grid_origin + ((max(int(begin), grid_origin) - grid_origin) // step) * step
    # The risk sits beyond the excursion the confirming candle rejected: the
    # highest high seen so far for a short, the lowest low for a long.
    band_high = None
    band_low = None
    for start in range(first, min(int(end), first + CONFIRM_HORIZON_MIN * NS_MINUTE), step):
        rows = _bars(market, start, start + step, 60)
        highs = [_d(row.get("H")) for row in rows if _d(row.get("H")) is not None]
        lows = [_d(row.get("L")) for row in rows if _d(row.get("L")) is not None]
        closes = [_d(row.get("C")) for row in rows if _d(row.get("C")) is not None]
        if not closes or not highs or not lows:
            continue
        bar_hi, bar_lo, close = max(highs), min(lows), closes[-1]
        band_high = bar_hi if band_high is None else max(band_high, bar_hi)
        band_low = bar_lo if band_low is None else min(band_low, bar_lo)
        if int(start + step) <= int(begin):
            continue
        if (close < level) if side == "short" else (close > level):
            band = band_high if side == "short" else band_low
            return {"entry": close, "at": int(start + step), "extreme": band}
    return None



# ---------------------------------------------------------------------------
# fills at a line
#
# One mechanic runs through every play the author prints: a drawn line is
# taken and price fails back through it, and he is in on the failure. His
# execution, in his own words (Time-Based ranges Framework pp.25-29): "Market
# Order ... this is what I mostly use during high volatility"; "Stop Order: I
# use this preset frequently"; "Generally I don't use Limit Orders"; and the
# entry models he "usually wait[s] for during reversals" are the 2/3/5-minute
# three-candle orderblock ("candle 3 closes above candle 2 ... confirms the set
# up") and the rejection block ("closure of the candle above the sweep candle
# confirms"). So the fills of one failure are:
#   stop_at_line      the stop order AT the line, triggered as price fails back
#                     through it (2025-12-30 25,690 on the low's reclaim,
#                     2026-08-28 29,592 at R-Lo, 2026-07-27 the EQ tag);
#   stop_at_next_line the stop at the next drawn line in the trade's direction
#                     after the failure (2025-10-13 the lower quadrant 24,768);
#   failure_close     the market order at the close of the minute that fails
#                     back through;
#   two_minute_close  the close of the fixed-grid two-minute candle back
#                     through (2026-07-10 29,809);
#   signature_close / rejection_close  the orderblock / rejection-block
#                     confirmation of the manual (2025-01-28 21,241.75,
#                     2025-10-13 24,848.50);
#   next_bar_open     FITTED: the turn of the tagging bar, filled at the next
#                     open.
# They are alternative fills of ONE opportunity; the selection layer chooses
# among them by the author's own tickets (MODE_PREFERENCE).

FILL_MODES = ("stop_at_line", "stop_at_next_line", "failure_close", "two_minute_close", "signature_close", "rejection_close", "next_bar_open")


def _fill_modes(confirmed, level, *, limit_at=None):
    """Kept for the rules table: the alternative fills of one signature."""
    if confirmed is None:
        return [(mode, None, None) for mode in ("at_level", "signature_close", "rejection_close")]
    out = [("at_level", level, int(limit_at) if limit_at is not None else confirmed["at"]), ("signature_close", confirmed["entry"], confirmed["at"])]
    if confirmed.get("signal_close") is not None:
        out.append(("rejection_close", confirmed["signal_close"], int(confirmed.get("signal_at") or confirmed["at"])))
    return out


def _touch_after(market, *, level: Decimal, side: str, begin: int, end: int) -> dict[str, Any] | None:
    """The first bar after ``begin`` whose range covers the level."""
    for row in _bars(market, begin, end, 60):
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None:
            continue
        if lo <= level <= hi:
            return row
    return None


def _stop_through(market, *, level: Decimal, side: str, begin: int, end: int) -> dict[str, Any] | None:
    """The stop order at the line: the first bar from ``begin`` (price beyond
    the line) that trades back through it -- a buy stop is triggered by a bar
    whose high reaches up to the line, a sell stop by a bar whose low reaches
    down to it."""
    for row in _bars(market, begin, end, 60):
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None:
            continue
        if (hi >= level) if side == "long" else (lo <= level):
            return row
    return None


def _session_orders(market):
    """Aggressor orders of the account day (fills grouped by event timestamp
    and side), from the trade parquet; cached per session in the process."""
    key = str(getattr(market, "day", None))
    if key in _ORDERS_CACHE:
        return _ORDERS_CACHE[key]
    orders = None
    try:
        import importlib.util as _ilu

        spec = _ilu.spec_from_file_location("sires_levels_fit", Path(__file__).resolve().parents[6] / "implementation/tools/sires_levels_fit.py")
        fit = _ilu.module_from_spec(spec)
        spec.loader.exec_module(fit)
        orders = fit.orders_between(key, int(market.start), int(market.end))
    except Exception:
        orders = None
    if len(_ORDERS_CACHE) > 4:
        _ORDERS_CACHE.pop(next(iter(_ORDERS_CACHE)))
    _ORDERS_CACHE[key] = orders
    return orders


def _big_print_fill(market, *, level: Decimal, side: str, begin: int, end: int) -> dict[str, Any] | None:
    """The first executed order at or above the BigTrades threshold within
    BIG_PRINT_POINTS of the level between ``begin`` and ``end``: the fill is
    the print's price, decided when its minute closes."""
    orders = _session_orders(market)
    if orders is None or len(orders) == 0:
        return None
    london_end = _at(market, "09:30")
    lo, hi = float(level - BIG_PRINT_POINTS), float(level + BIG_PRINT_POINTS)
    sub = orders[(orders["t"] >= int(begin)) & (orders["t"] < int(end)) & (orders["hi"] >= lo) & (orders["lo"] <= hi)]
    for row in sub.itertuples(index=False):
        threshold = BIGTRADES_LONDON if int(row.t) < london_end else BIGTRADES_NY
        if int(row.size) >= threshold:
            at = (int(row.t) // NS_MINUTE + 1) * NS_MINUTE
            return {"mode": "big_print", "entry": Decimal(str((float(row.lo) + float(row.hi)) / 2)).quantize(TICK), "at": at, "evidence_at": at, "print_size": int(row.size), "print_side": str(row.side)}
    return None


def _line_failure_fills(market, *, level: Decimal, side: str, cycle: Mapping[str, Any], end: int, evidence_at: int, internal: Decimal | None = None) -> list[dict[str, Any]]:
    """The fills of one failure of a line (the sweep bar, its extreme and the
    bar that closes back through are in ``cycle``). ``internal`` is the next
    drawn line beyond the failed one in the trade's direction: the author
    rests a limit there too and scales in at the lines (2025-10-13 buys the
    lower quadrant 24,768 after the low 24,731 was swept and reclaimed)."""
    fills: list[dict[str, Any]] = []
    extreme = _d(cycle.get("extreme"))
    sweep = cycle.get("sweep") or {}
    reclaim = cycle.get("reclaim")
    stop = None if extreme is None else ((extreme - STOP_BEYOND_EXTREME) if side == "long" else (extreme + STOP_BEYOND_EXTREME))
    if reclaim is not None:
        at = int(reclaim.get("known_at") or reclaim.get("end"))
        close = _d(reclaim.get("C"))
        if close is not None:
            fills.append({"mode": "failure_close", "entry": close, "at": at, "stop": stop, "evidence_at": at})
        # the stop order at the line is triggered inside the bar that comes
        # back through it: the first bar after the sweep bar that reaches the
        # line, which is the reclaim bar itself at the latest
        crossing = _stop_through(market, level=level, side=side, begin=int(sweep.get("end") or at) if sweep else at, end=at + NS_MINUTE) or reclaim
        fills.append({"mode": "stop_at_line", "entry": level, "at": int(crossing.get("known_at") or crossing.get("end")), "stop": stop, "evidence_at": int(crossing.get("known_at") or crossing.get("end"))})
        if internal is not None and sign(side) * (internal - level) > 0:
            crossing = _stop_through(market, level=internal, side=side, begin=at, end=end)
            if crossing is not None:
                fills.append({"mode": "stop_at_next_line", "entry": internal, "at": int(crossing.get("known_at") or crossing.get("end")), "stop": stop, "evidence_at": at, "internal": internal})
    two = _two_minute_reclaim(market, level=level, side=side, begin=int(sweep.get("start") or evidence_at), end=end) if sweep else None
    if two is not None:
        fills.append({"mode": "two_minute_close", "entry": two["entry"], "at": int(two["at"]), "stop": (two["extreme"] + STOP_BEYOND_EXTREME) if side == "short" else (two["extreme"] - STOP_BEYOND_EXTREME), "evidence_at": int(two["at"])})
    if sweep:
        pack = confirm_pack(market, int(sweep["end"]), side, level, min(end, int(sweep["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))
        confirmed = pack.get("confirmed")
        if confirmed is not None:
            fills.append({"mode": "signature_close", "entry": confirmed["entry"], "at": int(confirmed["at"]), "stop": confirmed["stop"], "evidence_at": int(confirmed["at"]), "signature": confirmed.get("kind"), "pack": pack})
            if confirmed.get("signal_close") is not None:
                fills.append({"mode": "rejection_close", "entry": confirmed["signal_close"], "at": int(confirmed.get("signal_at") or confirmed["at"]), "stop": confirmed["stop"], "evidence_at": int(confirmed.get("signal_at") or confirmed["at"]), "signature": confirmed.get("kind"), "pack": pack})
        turn = _spike_turn(market, level=level, side=side, bar=sweep, end=end)
        if turn is not None:
            fills.append({"mode": "next_bar_open", "entry": turn["entry"], "at": int(turn["at"]), "stop": turn["stop"], "evidence_at": int(turn["at"]), "fitted": True})
        if BIG_PRINT_CONFIRMATION:
            big = _big_print_fill(market, level=level, side=side, begin=int(sweep.get("start") or evidence_at), end=min(end, int(sweep["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))
            if big is not None:
                fills.append({**big, "stop": stop})
    return fills


def _contact_fills(market, *, level: Decimal, side: str, contact: Mapping[str, Any], end: int, placed_at: int) -> list[dict[str, Any]]:
    """The fills at a line REACHED after the evidence that put the order there
    (a projection line reached after the edge broke, a P-zone entered): the
    limit at the line on the touch, the signature at the line, the turn of the
    tagging bar."""
    fills: list[dict[str, Any]] = []
    lo, hi = _d(contact.get("L")), _d(contact.get("H"))
    touch_at = int(contact.get("known_at") or contact.get("end"))
    if lo is not None and hi is not None:
        # the line is reached; the stop order at the line is triggered as price
        # comes back through it -- the touching bar itself when it closes back
        # on the entry side, else the first later bar that reaches the line
        close = _d(contact.get("C"))
        back = close is not None and ((close > level) if side == "long" else (close < level))
        crossing = contact if back else _stop_through(market, level=level, side=side, begin=touch_at, end=end)
        if crossing is not None:
            c_lo, c_hi = _d(crossing.get("L")), _d(crossing.get("H"))
            extreme = min(lo, c_lo if c_lo is not None else lo) if side == "long" else max(hi, c_hi if c_hi is not None else hi)
            fills.append({"mode": "stop_at_line", "entry": level, "at": int(crossing.get("known_at") or crossing.get("end")), "stop": (extreme - STOP_BEYOND_EXTREME) if side == "long" else (extreme + STOP_BEYOND_EXTREME), "evidence_at": max(int(placed_at), int(crossing.get("known_at") or crossing.get("end")))})
    pack = confirm_pack(market, int(contact["end"]), side, level, min(end, int(contact["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))
    confirmed = pack.get("confirmed")
    if confirmed is not None:
        fills.append({"mode": "signature_close", "entry": confirmed["entry"], "at": int(confirmed["at"]), "stop": confirmed["stop"], "evidence_at": int(confirmed["at"]), "signature": confirmed.get("kind"), "pack": pack})
        if confirmed.get("signal_close") is not None:
            fills.append({"mode": "rejection_close", "entry": confirmed["signal_close"], "at": int(confirmed.get("signal_at") or confirmed["at"]), "stop": confirmed["stop"], "evidence_at": int(confirmed.get("signal_at") or confirmed["at"]), "signature": confirmed.get("kind"), "pack": pack})
    turn = _spike_turn(market, level=level, side=side, bar=contact, end=end)
    if turn is not None:
        fills.append({"mode": "next_bar_open", "entry": turn["entry"], "at": int(turn["at"]), "stop": turn["stop"], "evidence_at": int(turn["at"]), "fitted": True})
    if BIG_PRINT_CONFIRMATION:
        big = _big_print_fill(market, level=level, side=side, begin=int(contact.get("start") or touch_at), end=min(end, int(contact["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))
        if big is not None:
            lo_c, hi_c = _d(contact.get("L")), _d(contact.get("H"))
            extreme = lo_c if side == "long" else hi_c
            fills.append({**big, "stop": None if extreme is None else ((extreme - STOP_BEYOND_EXTREME) if side == "long" else (extreme + STOP_BEYOND_EXTREME)), "evidence_at": max(int(placed_at), int(big["at"]))})
    return fills


def _first_break(market, *, begin: int, end: int, edge: Decimal, side: str) -> dict[str, Any] | None:
    """The first bar that trades beyond the edge (above it for a short, below it for a long)."""
    for row in _bars(market, begin, end, 60):
        hi, lo = _d(row.get("H")), _d(row.get("L"))
        if side == "short" and hi is not None and hi > edge:
            return row
        if side == "long" and lo is not None and lo < edge:
            return row
    return None


def _forward_objective(rungs: Sequence[Mapping[str, Any]], entry: Decimal, side: str) -> Decimal | None:
    for row in rungs:
        price = _d(row.get("price"))
        if price is not None and sign(side) * (price - entry) > 0:
            return price
    return None


def _nearest_drawn(context: Mapping[str, Any], entry: Decimal, side: str, known_by: int) -> Decimal | None:
    forward = [
        row["price"]
        for row in context.get("levels") or []
        if int(row["known_at"]) <= known_by and sign(side) * (row["price"] - entry) > 0 and row["kind"] not in {"eq", "q25", "q75", "range_open", "prth_poc"}
    ]
    if not forward:
        return None
    return min(forward) if side == "long" else max(forward)


def _line_episodes(
    market,
    context: Mapping[str, Any],
    *,
    branch: str,
    side: str,
    level: Decimal,
    kind: str,
    location_kind: str,
    reference: Mapping[str, Any] | None,
    trigger: Mapping[str, Any] | None,
    fills: Sequence[Mapping[str, Any]],
    objective: Any,
    begin: int,
    cycle: int,
    location_ok: bool = True,
    location_reason: str | None = None,
    extra_values: Mapping[str, Any] | None = None,
    extra_location: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """One episode per alternative fill of one opportunity at one line."""
    out: list[dict[str, Any]] = []
    rows = list(fills) if (fills and location_ok) else [None]
    for fill in rows:
        entry = None if fill is None else _d(fill.get("entry"))
        # the decision is made when the fill AND its evidence are both on the
        # tape (a stop at the line can fill inside the sweep bar whose close is
        # the evidence; London flagged five such stamps in 218 sessions)
        at_ns = None if fill is None else max(int(fill["at"]), int(fill.get("evidence_at") or fill["at"]))
        stop = None if fill is None else _d(fill.get("stop"))
        mode = None if fill is None else fill["mode"]
        target = None
        if entry is not None:
            target = objective(entry) if callable(objective) else _forward_objective(objective, entry, side)
        stages = [
            _context_stage(context, begin, branch=branch, location_kind=location_kind),
            _stage("reference", "pass", int((reference or {}).get("known_at") or begin), id=(reference or {}).get("id"), level=level, kind=kind),
            _stage(
                "location",
                "pass" if (trigger is not None and location_ok) else "fail",
                None if trigger is None else int(trigger["start"]),
                level=level,
                kind=kind,
                location_kind=location_kind,
                reason=None if (trigger is not None and location_ok) else (location_reason or "line_not_taken_in_the_window"),
                **{k: v for k, v in (extra_location or {}).items()},
            ),
            _stage(
                "trigger",
                "pass" if trigger is not None else "fail",
                None if trigger is None else int(trigger.get("known_at") or trigger.get("end")),
                **(
                    {
                        "modal_window": list(MODAL_WINDOW),
                        "in_modal_window": None if trigger is None else bool(_at(market, MODAL_WINDOW[0]) <= int(trigger["start"]) < _at(market, MODAL_WINDOW[1])),
                    }
                    if branch == "judas_reversal"
                    else {}
                ),
            ),
            _stage(
                "confirmation",
                "pass" if fill is not None else "fail",
                None if fill is None else int(fill.get("evidence_at") or fill["at"]),
                mode=mode,
                signature=None if fill is None else fill.get("signature"),
                fitted=None if fill is None else bool(fill.get("fitted")),
                reason=None if fill is not None else "no_fill_after_the_failure",
            ),
            _stage("risk", "pass" if entry is not None and stop is not None and sign(side) * (entry - stop) > 0 else "fail", at_ns, entry=entry, stop=stop),
            _stage("objective", "pass" if entry is not None and target is not None and sign(side) * (target - entry) > 0 else "fail", at_ns, first_objective=target),
            _stage("management", "pass", at_ns, scale_out="along the ladder"),
        ]
        values = {
            "reference_px": level,
            "reference_kind": kind,
            "reference_id": (reference or {}).get("id"),
            "location_kind": location_kind,
            "cycle": cycle,
            "confirmation_mode": mode,
            "signature": None if fill is None else fill.get("signature"),
        }
        if extra_values:
            values.update(extra_values)
        out.append(
            _episode(
                market,
                branch=branch,
                side=side,
                stages=stages,
                decision_at=at_ns,
                entry=entry,
                stop=stop,
                target=target,
                reference=reference,
                trigger=trigger,
                values=values,
                geometry={"first_objective": target},
            )
        )
    return out


def _sweep_levels(context: Mapping[str, Any], *, sides: tuple[str, ...] = ("long", "short"), exclude_box: bool = False) -> list[dict[str, Any]]:
    out = []
    for row in context.get("levels") or []:
        if row.get("role") != "sweep":
            continue
        if exclude_box and row["kind"] in {"box_low", "box_high"}:
            continue
        if row["side"] in sides:
            out.append(row)
    return out


def _coincident(context: Mapping[str, Any], price: Decimal, *, exclude_kind: str | None = None, beyond: Decimal | None = None, side: str | None = None) -> list[str]:
    """Drawn levels within LEVEL_COINCIDENCE of ``price``. With ``beyond`` and
    ``side`` only levels on the far side of that edge count: the exhaustion
    area lies beyond the box edge, a level inside the box does not make a
    5-point poke of the edge a Judas."""
    hits = []
    for row in context.get("levels") or []:
        if row["kind"] == exclude_kind or row.get("role") not in {"sweep", "marker"}:
            continue
        if beyond is not None and side is not None:
            outside = (row["price"] >= beyond) if side == "short" else (row["price"] <= beyond)
            if not outside:
                continue
        if abs(row["price"] - price) <= LEVEL_COINCIDENCE:
            hits.append(row["kind"])
    return hits


def _box_objective(box: Mapping[str, Any], side: str):
    return objective_ladder(box, side)


def _trend_objective(box: Mapping[str, Any], side: str) -> list[dict[str, Any]]:
    """Single-break days: the objective is the far edge, then the projections
    (J12: "the projection, not the range edge" for the purged case)."""
    if side == "short":
        return [
            {"name": "box_low", "price": box["low"]},
            {"name": "minus_0.5", "price": box["ladder"]["minus_0.5"]},
            {"name": "minus_1", "price": box["ladder"]["minus_1"]},
            {"name": "minus_1.33", "price": box["ladder"]["minus_1.33"]},
        ]
    return [
        {"name": "box_high", "price": box["high"]},
        {"name": "plus_0.5", "price": box["ladder"]["plus_0.5"]},
        {"name": "plus_1", "price": box["ladder"]["plus_1"]},
        {"name": "plus_1.33", "price": box["ladder"]["plus_1.33"]},
    ]


# ---------------------------------------------------------------------------
# the plays


def _scan_judas_reversal(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The double-break / Judas day (audit §1.1): one edge is swept, the sweep
    extends into the exhaustion area (the 0.33-0.66 band, the 0.5 projection,
    a P-zone, an overnight / London / Asia / prior-day extreme, an EVRange
    line), price fails back and reverses through the mid toward the untouched
    edge. Three location kinds, each traded on the failure of the line:

    * the box edge, every raid of it ("first stage of the move taking both
      high and low of the range before the full reversal", JR p.20,
      2025-10-13: the 09:05 short is an 11-point sweep of the R-Hi on a
      147-point range); the depth class and the coincident exhaustion levels
      are recorded, not gated;
    * a projection line beyond the edge, reached after the edge broke;
    * a liquidity level the author has drawn, swept and failed.
    Internals (EQ, quadrants, range open) are never Judas locations."""
    context = session_context(market)
    box = context.get("box")
    if box is None:
        return [], [{"reason": "ny_range_unavailable", "branch": "judas_reversal"}]
    begin, end = _at(market, NY_ACTION[0]), _at(market, NY_ACTION[1])
    end = min(end, int(market.end))
    episodes: list[dict[str, Any]] = []

    # 1. the box edges. Every raid of the edge is a Judas location: the author
    # sells the 2025-10-13 R-Hi at 09:05 on an 11-point sweep of a 147-point
    # range ("taking both high and low of the range before the full reversal",
    # JR p.20). The first two raids of an edge are the opportunities; how far
    # the raid reached (its depth class, the exhaustion levels it met) is
    # recorded on the episode for the context study, not used as a gate.
    raid_end = min(_at(market, JUDAS_RAID_WINDOW[1]), end)
    for name, side, level in (("box_high", "short", box["high"]), ("box_low", "long", box["low"])):
        for cycle in sweep_cycles(market, level=level, side=side, begin=_at(market, JUDAS_RAID_WINDOW[0]), end=raid_end, max_cycles=2):
            extreme = cycle["extreme"]
            depth = (level - extreme) if side == "long" else (extreme - level)
            klass = depth_class(depth, box["width"])
            hits = _coincident(context, extreme, exclude_kind=name, beyond=level, side=side)
            reached = True
            fills = _line_failure_fills(market, level=level, side=side, cycle=cycle, end=end, evidence_at=int(cycle["sweep"]["end"]), internal=box["q25"] if side == "long" else box["q75"])
            episodes.extend(
                _line_episodes(
                    market, context,
                    branch="judas_reversal", side=side, level=level, kind=name, location_kind="edge_sweep",
                    reference=box, trigger=cycle["sweep"], fills=fills, objective=_box_objective(box, side), begin=begin,
                    cycle=int(cycle["cycle"]), location_ok=reached, location_reason=None if reached else "sweep_short_of_exhaustion_area",
                    extra_values={"sweep_extreme": extreme, "depth_class": klass, "coincident_levels": hits},
                    extra_location={"sweep_extreme": extreme, "depth_points": depth, "depth_class": klass, "coincident_levels": hits},
                )
            )

    # 2. the projection lines beyond the edge, reached after the edge broke
    band_drawn = (_as_day(market) or date.min) >= MEAN_REVERSAL_BAND_FROM
    for name, side, edge in (("plus_0.33", "short", box["high"]), ("plus_0.5", "short", box["high"]), ("plus_0.66", "short", box["high"]),
                             ("minus_0.33", "long", box["low"]), ("minus_0.5", "long", box["low"]), ("minus_0.66", "long", box["low"])):
        if not band_drawn and name not in {"plus_0.5", "minus_0.5"}:
            continue
        line = box["ladder"][name]
        first_break = _first_break(market, begin=begin, end=end, edge=edge, side=side)
        if first_break is None:
            continue
        contacts = level_contacts(market, level=line, begin=int(first_break["start"]), end=end, departure=box["width"] / 10)
        for index, contact in enumerate(contacts):
            fills = _contact_fills(market, level=line, side=side, contact=contact, end=end, placed_at=int(first_break["start"]))
            episodes.extend(
                _line_episodes(
                    market, context,
                    branch="judas_reversal", side=side, level=line, kind=name, location_kind="exhaustion_projection",
                    reference=box, trigger=contact, fills=fills, objective=_box_objective(box, side), begin=begin, cycle=index,
                    extra_values={"edge_broken_at": int(first_break["start"])},
                )
            )

    # 3. a drawn liquidity level BEYOND the box edge, swept and failed (the
    # overnight, London, Asia and prior-day extremes he deletes when purged).
    # An extreme lying inside the 6-9 range is an objective, not a location:
    # the mid-box London/Asia extremes on 2026-07-06, 2025-09-09 and
    # 2026-07-10 are where he takes profit.
    for row in _sweep_levels(context, exclude_box=True):
        side, level = row["side"], row["price"]
        if int(row["known_at"]) > begin:
            continue
        outside = (level > box["high"]) if side == "short" else (level < box["low"])
        if not outside:
            continue  # inside the range the extremes are objectives; the raid he fades is beyond the edge
        for cycle in sweep_cycles(market, level=level, side=side, begin=begin, end=end, max_cycles=2):
            fills = _line_failure_fills(market, level=level, side=side, cycle=cycle, end=end, evidence_at=int(cycle["sweep"]["end"]))
            episodes.extend(
                _line_episodes(
                    market, context,
                    branch="judas_reversal", side=side, level=level, kind=row["kind"], location_kind="swept_liquidity",
                    reference=box, trigger=cycle["sweep"], fills=fills, objective=_box_objective(box, side), begin=begin,
                    cycle=int(cycle["cycle"]), extra_values={"sweep_extreme": cycle["extreme"]},
                )
            )
    return episodes, []


def _scan_judas_outbound(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The single-break continuation at the open: the opening drive breaks the
    box edge in the day's direction and the trade runs with it from the retest
    of the broken edge to the projection (audit §1.1 'Trade #1'; no dated
    ticket prints this trade after the 2026-07-16 re-read)."""
    context = session_context(market)
    box = context.get("box")
    read = context.get("read") or {}
    if box is None:
        return [], []
    direction = read.get("trend_direction")
    if read.get("classification") != "single_break" or direction is None:
        return [], [{"reason": "read_has_no_break_direction", "branch": "judas_outbound", "play": "single_break"}]
    open_ns, end = _at(market, "09:30"), min(_at(market, "10:30"), int(market.end))
    edge = box["low"] if direction == "short" else box["high"]
    rows = _bars(market, open_ns, end, 60)
    break_bar = _first_break(market, begin=open_ns, end=end, edge=edge, side="long" if direction == "short" else "short")
    if break_bar is None:
        return [], []
    retest = _touch_after(market, level=edge, side=direction, begin=int(break_bar["end"]), end=end)
    fills = []
    if retest is not None:
        stop = (edge + STOP_BEYOND_EXTREME) if direction == "short" else (edge - STOP_BEYOND_EXTREME)
        fills.append({"mode": "stop_at_line", "entry": edge, "at": int(retest.get("known_at") or retest.get("end")), "stop": stop, "evidence_at": int(break_bar["end"])})
    return _line_episodes(
        market, context,
        branch="judas_outbound", side=direction, level=edge, kind="box_low" if direction == "short" else "box_high", location_kind="broken_edge_retest",
        reference=box, trigger=break_bar, fills=fills, objective=_trend_objective(box, direction)[1:], begin=open_ns, cycle=0,
    ), []


def _eq_lines(market, branch: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """The lines, sides, window and objective ladder of one EQ play on the day,
    or the omission that gates it (the plan `_scan_eq_branch` runs)."""
    context = session_context(market)
    box = context.get("box")
    read = context.get("read") or {}
    if box is None:
        return None, []
    direction = read.get("trend_direction")
    if branch in {"single_extended", "single_purged"}:
        sides = ("long", "short") if branch == "single_extended" or direction is None else (direction,)
        begin = _at(market, "09:00" if branch == "single_extended" else "09:30")
        end = min(_at(market, SINGLE_EXTENDED_END if branch == "single_extended" else SINGLE_PURGED_END), int(market.end))
        lines = [("eq", box["eq"])] if branch == "single_extended" else [("eq", box["eq"]), ("q25", box["q25"]), ("q75", box["q75"]), ("range_open", box["range_open"])]
        if branch == "single_purged":
            span = _span(_bars(market, _at(market, "09:30"), _at(market, "09:45"), 60), known_at=_at(market, "09:45"))
            if span is not None:
                width = span["high"] - span["low"]
                lines += [("or15_mid", (span["low"] + span["high"]) / 2), ("or15_q25", span["low"] + width / 4), ("or15_q75", span["low"] + width * 3 / 4)]
            # Phase 1.5 candidate: the projections as retest lines on the
            # expansion day (2026-05-15: longs at the +0.33 projection at 12:46
            # and 12:55 after the break above the range); B0.3 draws none
            for name in PURGED_PROJECTION_LINES:
                if box["ladder"].get(name) is not None:
                    lines.append((name, box["ladder"][name]))
        objective = {side: _trend_objective(box, side) for side in ("long", "short")}
    else:
        sides = ("long", "short")
        begin, end = _at(market, "09:30"), min(_at(market, "16:00"), int(market.end))
        lines = [("box_low", box["low"]), ("box_high", box["high"])]
        value = context.get("prior_value") or {}
        for kind, key in (("prth_val", "val"), ("prth_vah", "vah"), ("prth_poc", "poc")):
            price = _d(value.get(key))
            if price is not None:
                lines.append((kind, price))
        # "open inside prior RTH value: range scalps" (2026-07-10): the scalps
        # are taken at the range's own lines -- the quadrants and the EQ beside
        # the edges and the value edges (his 11:05 long sits on the lower
        # quadrant 29,800 / his pRTHVAL 29,790); on a big range (>=0.8%) the EQ
        # and quadrants are traded the same way (2026-09-02).
        if read.get("big_range") or read.get("open_inside_value"):
            lines += [("eq", box["eq"]), ("q25", box["q25"]), ("q75", box["q75"])]
        objective = {"long": [{"name": "eq", "price": box["eq"]}, {"name": "box_high", "price": box["high"]}, {"name": "plus_0.5", "price": box["ladder"]["plus_0.5"]}],
                     "short": [{"name": "eq", "price": box["eq"]}, {"name": "box_low", "price": box["low"]}, {"name": "minus_0.5", "price": box["ladder"]["minus_0.5"]}]}
        if not (read.get("open_inside_value") or read.get("big_range")):
            return None, [{"reason": "rotation_needs_inside_value_or_big_range", "branch": branch, "play": "big_range_eq"}]
    return {"context": context, "box": box, "sides": sides, "begin": begin, "end": end, "lines": lines, "objective": objective, "direction": direction}, []


def _scan_eq_branch(market, branch: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The plays traded at the box internals and the prior value area.

    single_extended: the single-break day, from 09:00 -- the EQ / quadrant /
    range-open retest in the break direction after the line is taken and fails
    (2026-07-27 sells the EQ tag at 09:02; 2026-07-16 sells the failure of the
    EQ at 09:35), objective the far edge then the projections.
    single_purged: the same lines from 09:30 on a day that opens outside prior
    value on the purged side (2026-07-28 "RTH open below the prior RTH value
    low"), objective the projection (J12), the 15-minute opening range mid and
    quartiles added (J3).
    internal_rotation: "open inside prior RTH value: range scalps" (2026-07-10)
    -- the box edges and the prior value edges, both ways, from 09:30; on a big
    6-9 range (>=0.8%, 2026-09-02) the EQ and quadrants join it."""
    plan, omissions = _eq_lines(market, branch)
    if plan is None:
        return [], omissions
    context, box, sides, begin, end, lines, objective, direction = (plan[key] for key in ("context", "box", "sides", "begin", "end", "lines", "objective", "direction"))
    episodes: list[dict[str, Any]] = []
    for kind, level in lines:
        if level is None:
            continue  # a line the day did not draw (no 15-minute opening range, no prior value)
        for side in sides:
            if side is None:
                continue
            known = box["known_at"] if not kind.startswith("or15") else _at(market, "09:45")
            start = max(begin, int(known))
            for cycle in sweep_cycles(market, level=level, side=side, begin=start, end=end, max_cycles=4 if branch == "internal_rotation" else 2):
                fills = _line_failure_fills(market, level=level, side=side, cycle=cycle, end=end, evidence_at=int(cycle["sweep"]["end"]))
                episodes.extend(
                    _line_episodes(
                        market, context,
                        branch=branch, side=side, level=level, kind=kind, location_kind="line_failure",
                        reference=box, trigger=cycle["sweep"], fills=fills, objective=objective[side], begin=begin,
                        cycle=int(cycle["cycle"]), extra_values={"trend_direction": direction, "range_bin": (context.get("range_class") or {}).get("bin")},
                    )
                )
    if branch == "single_purged":
        episodes.extend(_value_layer_episodes(market, context, branch))
    return episodes, []


def _value_layer_episodes(market, context: Mapping[str, Any], branch: str) -> list[dict[str, Any]]:
    """The same two plays on the value-area layer of the range (see
    VALUE_RANGE_WINDOW). ``extension_reaction``: once a value edge has broken,
    a resting limit at the 1.33 and at the 1.66 projection beyond it, every
    contact its own opportunity (2026-05-19 buys the -1.66 at 10:22 and again
    at 10:51, "the -1.33/-1.66 band with absorption prints"). ``single_purged``:
    on the expansion day the broken value edge and the 0.33-0.66 projections
    are retested WITH the break (2026-05-15 buys the +0.33 retest at 12:46 and
    the reclaim from the value high at 12:55, "quick 80 points afternoon")."""
    box = box_geometry(market, "ny_value")
    if box is None:
        return []
    begin = max(_at(market, VALUE_RANGE_ACTION[0]), int(box["known_at"]))
    end = min(_at(market, VALUE_RANGE_ACTION[1]), int(market.end))
    ladder, low, high = box["ladder"], box["low"], box["high"]
    episodes: list[dict[str, Any]] = []
    if branch == "extension_reaction":
        for name, side, edge in (("plus_1.33", "short", high), ("plus_1.66", "short", high), ("minus_1.33", "long", low), ("minus_1.66", "long", low)):
            first_break = _first_break(market, begin=begin, end=end, edge=edge, side=side)
            if first_break is None:
                continue
            for index, contact in enumerate(level_contacts(market, level=ladder[name], begin=int(first_break["start"]), end=end, departure=box["width"] / 10)):
                fills = _contact_fills(market, level=ladder[name], side=side, contact=contact, end=end, placed_at=int(first_break["start"]))
                episodes.extend(_line_episodes(market, context, branch=branch, side=side, level=ladder[name], kind=f"value_{name}", location_kind="exhaustion_projection", reference=box, trigger=contact, fills=fills, objective=objective_ladder(box, side), begin=begin, cycle=index))
    elif branch == "single_purged":
        for side, edge, names in (("long", high, ("plus_0.33", "plus_0.5", "plus_0.66")), ("short", low, ("minus_0.33", "minus_0.5", "minus_0.66"))):
            broke = _first_break(market, begin=begin, end=end, edge=edge, side="short" if side == "long" else "long")
            if broke is None:
                continue
            objective = _trend_objective(box, side)
            for kind, level in [("value_high" if side == "long" else "value_low", edge)] + [(f"value_{name}", ladder[name]) for name in names]:
                index = 0
                for seg_from, seg_to in VALUE_RANGE_SEGMENTS:
                    start, stop_at = max(int(broke["end"]), _at(market, seg_from)), min(end, _at(market, seg_to))
                    if start >= stop_at:
                        continue
                    for contact in level_contacts(market, level=level, begin=start, end=stop_at, departure=box["width"] / 10):
                        fills = _contact_fills(market, level=level, side=side, contact=contact, end=stop_at, placed_at=start)
                        episodes.extend(_line_episodes(market, context, branch=branch, side=side, level=level, kind=kind, location_kind="line_test", reference=box, trigger=contact, fills=fills, objective=objective, begin=begin, cycle=index))
                        index += 1
    return episodes


def _scan_other_session(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """London: the overnight box that closes at 03:00, traded 03:00-07:00 with
    the same internals and projections; the drawn liquidity levels are live
    through the London session from 02:00 (2025-05-23 buys the prior RTH low
    at 02:20)."""
    context = session_context(market)
    london = box_geometry(market, "london")
    begin, end = _at(market, LONDON_TRADE[0]), min(_at(market, LONDON_TRADE[1]), int(market.end))
    live_from = _at(market, "02:00")
    episodes: list[dict[str, Any]] = []
    if london is not None:
        ladder = london["ladder"]
        # the edges: a sweep that fails (the box low on 2025-10-08)
        for name, side, level in (("london_high", "short", london["high"]), ("london_low", "long", london["low"])):
            for cycle in sweep_cycles(market, level=level, side=side, begin=begin, end=end, max_cycles=2):
                fills = _line_failure_fills(market, level=level, side=side, cycle=cycle, end=end, evidence_at=int(cycle["sweep"]["end"]))
                if not fills:
                    touch = _touch_after(market, level=level, side=side, begin=begin, end=end)
                    if touch is not None:
                        fills = _contact_fills(market, level=level, side=side, contact=touch, end=end, placed_at=london["known_at"])
                episodes.extend(_line_episodes(market, context, branch="other_session", side=side, level=level, kind=name, location_kind="edge_sweep", reference=london, trigger=cycle["sweep"], fills=fills, objective=objective_ladder(london, side), begin=begin, cycle=int(cycle["cycle"])))
            # the edge tested from inside without a sweep: a resting limit at the edge
            if not sweep_cycles(market, level=level, side=side, begin=begin, end=end, max_cycles=1):
                touch = _touch_after(market, level=level, side=side, begin=begin, end=end)
                if touch is not None:
                    fills = _contact_fills(market, level=level, side=side, contact=touch, end=end, placed_at=london["known_at"])
                    episodes.extend(_line_episodes(market, context, branch="other_session", side=side, level=level, kind=name, location_kind="edge_test", reference=london, trigger=touch, fills=fills, objective=objective_ladder(london, side), begin=begin, cycle=0))
        # the internals: a line taken and failed, both ways (2025-10-06 and 10-07 buy the 25% line)
        for kind, level in (("eq", london["eq"]), ("q25", london["q25"]), ("q75", london["q75"])):
            for side in ("long", "short"):
                for cycle in sweep_cycles(market, level=level, side=side, begin=begin, end=end, max_cycles=2):
                    fills = _line_failure_fills(market, level=level, side=side, cycle=cycle, end=end, evidence_at=int(cycle["sweep"]["end"]))
                    episodes.extend(_line_episodes(market, context, branch="other_session", side=side, level=level, kind=kind, location_kind="line_failure", reference=london, trigger=cycle["sweep"], fills=fills, objective=objective_ladder(london, side), begin=begin, cycle=int(cycle["cycle"])))
        # the projections beyond the edge, reached after the edge broke (2026-06-05 buys the -1.66)
        for name, side, edge in (("plus_0.33", "short", london["high"]), ("plus_0.5", "short", london["high"]), ("plus_0.66", "short", london["high"]), ("plus_1.33", "short", london["high"]), ("plus_1.66", "short", london["high"]),
                                 ("minus_0.33", "long", london["low"]), ("minus_0.5", "long", london["low"]), ("minus_0.66", "long", london["low"]), ("minus_1.33", "long", london["low"]), ("minus_1.66", "long", london["low"])):
            line = ladder[name]
            first_break = _first_break(market, begin=begin, end=end, edge=edge, side=side)
            if first_break is None:
                continue
            for index, contact in enumerate(level_contacts(market, level=line, begin=int(first_break["start"]), end=end, departure=london["width"] / 10)):
                fills = _contact_fills(market, level=line, side=side, contact=contact, end=end, placed_at=int(first_break["start"]))
                episodes.extend(_line_episodes(market, context, branch="other_session", side=side, level=line, kind=name, location_kind="exhaustion_projection", reference=london, trigger=contact, fills=fills, objective=objective_ladder(london, side), begin=begin, cycle=index))
    # the drawn liquidity levels, live from 02:00
    for row in _sweep_levels(context, exclude_box=True):
        if not (row["kind"].startswith("prth_") or row["kind"][:2] in {"d1", "d2", "d3"}):
            continue  # the Asia / overnight extremes are the London box itself
        start = max(live_from, int(row["known_at"]))
        if start >= end:
            continue
        for cycle in sweep_cycles(market, level=row["price"], side=row["side"], begin=start, end=end, max_cycles=2):
            fills = _line_failure_fills(market, level=row["price"], side=row["side"], cycle=cycle, end=end, evidence_at=int(cycle["sweep"]["end"]))
            objective = (objective_ladder(london, row["side"]) if london is not None and int(cycle["sweep"]["start"]) >= int(london["known_at"]) else None)
            episodes.extend(
                _line_episodes(
                    market, context, branch="other_session", side=row["side"], level=row["price"], kind=row["kind"], location_kind="swept_liquidity",
                    reference={"id": f"jj-london-levels:{getattr(market, 'instrument_id', 'view')}:{_as_day(market)}", "known_at": int(row["known_at"])}, trigger=cycle["sweep"], fills=fills,
                    objective=(lambda entry, s=row["side"], known=int(cycle["sweep"]["end"]): _nearest_drawn(context, entry, s, known)) if objective is None else objective,
                    begin=start, cycle=int(cycle["cycle"]),
                )
            )
    if not episodes and london is None:
        return [], [{"reason": "london_range_unavailable", "branch": "other_session"}]
    return episodes, []


def _scan_pzone(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The P-zone play: a resting limit inside the zone the author drew
    (2026-01-09 buys 25,664.25 inside 25,655-25,665; 2026-01-02 at 09:22 in the
    09:00 T1 box), with the signature at the zone as the alternative fill.
    Printed zones where the author printed them; elsewhere the fitted recipe,
    labelled as an approximation."""
    context = session_context(market)
    box = context.get("box")
    zones = context.get("pzones") or []
    if not zones:
        return [], [{"reason": "pzone_generator_unavailable", "branch": "timed_pzone_reversal", "operand": "pzone_generator"}]
    omissions: list[dict[str, Any]] = []
    if PZONE_NODE_SNAP:
        zones, dropped = _pzones_on_nodes(market, zones)
        omissions.extend({"reason": "pzone_not_on_node_or_ledge", "branch": "timed_pzone_reversal", "operand": "pzone", "pzone": [str(z["low"]), str(z["high"])]} for z in dropped)
        if not zones:
            return [], omissions
    episodes: list[dict[str, Any]] = []
    price_at_nine = context.get("price_at_0900")
    for index, zone in enumerate(zones):
        anchor = zone.get("anchor", "09:00")
        begin = _at(market, anchor)
        end = min(_at(market, "12:00"), int(market.end))
        low, high = _d(zone["low"]), _d(zone["high"])
        side = zone.get("side") or ("long" if (price_at_nine is not None and high < price_at_nine) or (box is not None and high < box["eq"]) else "short")
        near = high if side == "long" else low
        contact = _touch_after(market, level=near, side=side, begin=begin, end=end)
        fills = [] if contact is None else _contact_fills(market, level=near, side=side, contact=contact, end=end, placed_at=begin)
        for fill in fills:
            if fill["mode"] == "stop_at_line":
                fill["mode"] = "zone_limit"
                fill["stop"] = (low - TICK) if side == "long" else (high + TICK)
        reference = {"id": f"pzone:{_as_day(market)}:{anchor}:{low}-{high}", "low": low, "high": high, "known_at": begin, "tier": zone.get("tier")}
        objective = (lambda entry, s=side, known=int((contact or {}).get("end") or begin): _nearest_drawn(context, entry, s, known)) if box is None else (
            [{"name": "box_low", "price": box["low"]}, {"name": "eq", "price": box["eq"]}, {"name": "box_high", "price": box["high"]}, {"name": "plus_0.5", "price": box["ladder"]["plus_0.5"]}]
            if side == "long" else [{"name": "box_high", "price": box["high"]}, {"name": "eq", "price": box["eq"]}, {"name": "box_low", "price": box["low"]}, {"name": "minus_0.5", "price": box["ladder"]["minus_0.5"]}]
        )
        episodes.extend(
            _line_episodes(
                market, context, branch="timed_pzone_reversal", side=side, level=near, kind=f"pzone_{zone.get('tier') or anchor}", location_kind="pzone",
                reference=reference, trigger=contact, fills=fills, objective=objective, begin=begin, cycle=index,
                extra_values={"pzone": [low, high], "pzone_anchor": anchor, "pzone_source": zone.get("source") or context.get("pzone_source")},
            )
        )
    return episodes, omissions


def _pzones_on_nodes(market, zones: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """FIND p.8: a P-zone is kept where it "sits on an HVN or on the shelf next
    to an LVN" of the profile built so far (18:00 to the zone's anchor); either
    edge of the band within PZONE_NODE_TOLERANCE of a node or ledge keeps it."""
    from trading_research.research.method_pack.profile_nodes import on_node_or_ledge

    kept, dropped = [], []
    payloads: dict[str, dict] = {}
    for zone in zones:
        anchor = zone.get("anchor", "09:00")
        if anchor not in payloads:
            payloads[anchor] = market.profile(_at(market, "18:00", -1), _at(market, anchor))
        payload = payloads[anchor]
        low, high = _d(zone["low"]), _d(zone["high"])
        if on_node_or_ledge(low, payload, PZONE_NODE_TOLERANCE) or on_node_or_ledge(high, payload, PZONE_NODE_TOLERANCE):
            kept.append(zone)
        else:
            dropped.append(zone)
    return kept, dropped


_SCANNERS = {
    "judas_reversal": _scan_judas_reversal,
    "judas_outbound": _scan_judas_outbound,
    "extension_reaction": _scan_extension_reaction,
    "other_session": _scan_other_session,
    "timed_pzone_reversal": _scan_pzone,
    "single_extended": lambda market: _scan_eq_branch(market, "single_extended"),
    "single_purged": lambda market: _scan_eq_branch(market, "single_purged"),
    "internal_rotation": lambda market: _scan_eq_branch(market, "internal_rotation"),
}

# The author's two sessions, each with its own thesis and its own cap (audit
# §1.1 clocks): London 03:00-06:00 on the overnight box, NY 09:00-12:00 with
# the extension entries running to 16:00.
SEGMENTS = {"london": ("02:00", "07:00"), "ny": ("09:00", "16:00")}
SELECTION_CLOCK = ("02:00", "16:00")
# The list is bounded by the opportunities (two per line and side, one
# position at a time), not by a count: 2026-07-10 "had a couple diabolical Ls
# and roundtrips" before the 11:05 rotation long (JR p.42).
# the single-break plays' action windows (Phase 1.5 timing axis: "same ranges,
# different layers" -- 2026-05-15's +0.33 projection retests at 12:46 and 12:55
# sit past the 12:00 end of the purged case)
PURGED_PROJECTION_LINES: tuple = ()
# Phase 1.5 confirmation candidate: a large executed order at the level
# (BigTrades: "I use a 100 threshold on NQ during NY and 75 during London",
# FIND p.9; "confirmation: ... large prints >= threshold", FIND p.12).
# B0.3 does not use it; 2026-05-19's -1.33 long sits on a 282-lot print.
BIG_PRINT_CONFIRMATION = False
# Phase 1.5 candidate: a resting limit at the extension band's own lines (the
# -1.66 long of 2025-09-09 at 10:35; the 2026-05-19 chart's long at the band
# on the 282-lot print), beside the signature confirmation B0.3 uses
EXTENSION_BAND_LIMIT = False
# Phase 1.5 candidate (FIND p.8): keep a P-zone band only where it "sits on an
# HVN or on the shelf next to an LVN" of the overnight profile (18:00 to the
# zone's anchor); a lone P-zone in air is not his trade
PZONE_NODE_SNAP = False
PZONE_NODE_TOLERANCE = Decimal("5")
BIGTRADES_NY = 100
BIGTRADES_LONDON = 75
BIG_PRINT_POINTS = Decimal("2")
_ORDERS_CACHE: dict = {}
SINGLE_EXTENDED_END = "10:30"
SINGLE_PURGED_END = "12:00"
NY_ROUND_TRIPS = 8
LONDON_ROUND_TRIPS = 4
# THE TRADED LIST. He takes one trade on 24 of his 27 ticket days and two on the other
# three; the list the caps above produced took twelve to fourteen (2026-09-18). His own
# words set the clocks and the counts:
#   "always terminating my trading session before 10am" (TBR p.8); "nothing beats being
#   done in the first 20 mins of market open" (JR p.41); "one and done on the early fade of
#   the range, highest probability of the time segment" (JR p.54); "done for the day at
#   open" (JR p.38);
#   after a failed setup "Exit and Observe ... Switch to Alternative Models ... or look for
#   opportunities in PM session" (TBR p.37), a re-entry "is considered to be plausible" on
#   expansive days (TBR p.24);
#   the extension band is the business of the hours after 10:00 (TBR p.21), the afternoon
#   of the day the morning consolidated (TBR p.36).
# Each window is (from, to, round trips): an attempt and one re-entry in the morning and in
# London, one trade in each later clock; a paid objective ends its own window. An add is
# size on the open thesis, not a setup, and is left to the sizing layer.
NY_TRADE_WINDOWS = (("09:00", "10:15", 2), ("10:15", "12:00", 1), ("12:00", "16:00", 1))
LONDON_TRADE_WINDOWS = (("02:00", "07:00", 2),)
MAX_PER_LINE = 2
# the executed list's policy (Phase 1.5 selection axis: varied by the population runner)
EDGE_FIRST = True
EXECUTED_ALLOW_ADDS: bool | str = False
EXECUTED_ALLOW_FLIPS = True
# The 0.33/0.66 mean-reversal band is drawn on the author's charts from
# December 2025 (audit §1.1: "the 'mean reversal' band, drawn from December
# 2025"); before that his projections are the 0.5 and the 1.33/1.66 band.
MEAN_REVERSAL_BAND_FROM = date(2025, 12, 1)
PLAY_CANDIDATES = {
    "double_break": ("judas_reversal", "extension_reaction"),
    "single_break": ("single_extended", "single_purged", "judas_outbound", "extension_reaction"),
    "unknown": ("judas_reversal", "extension_reaction", "single_extended", "single_purged", "judas_outbound"),
}


def _rec_branch(rec: Any) -> str | None:
    if isinstance(rec, Mapping):
        return rec.get("branch")
    return getattr(rec, "branch", None)


def selection_for(market, episodes, *, primary_play: str | None = None) -> dict[str, Any]:
    """The author's trade list: London and NY selected on their own clocks; in
    NY the day's play first (its own branches, in time order), the rotation
    play beside it when the read admits it; one position at a time; up to
    three entries a segment; a stopped idea may be followed by the next
    qualifying setup ("after a failed idea the author flips"); a full
    objective does not end the session (that rule is Green Bird's)."""
    start = getattr(market, "start", None)
    end = getattr(market, "end", None)
    bars = _bars(market, int(start), int(end), 60) if start is not None and end is not None else []
    context = session_context(market)
    read = context.get("read") or {}
    classification = primary_play if primary_play in PLAY_CANDIDATES else (read.get("classification") if read.get("classification") in PLAY_CANDIDATES else "unknown")
    if primary_play == "london":
        classification = read.get("classification") if read.get("classification") in PLAY_CANDIDATES else "unknown"
    branches = set(PLAY_CANDIDATES[classification])
    if read.get("open_inside_value") or read.get("big_range") or primary_play == "big_range_eq":
        branches.add("internal_rotation")
    if primary_play == "pzone":
        branches.add("timed_pzone_reversal")
    passing = [ep for ep in episodes if ep.get("research_verdict") == "pass"]
    # The CANDIDATE list is open: the day's play is a READ, not a gate. He takes a
    # rotation at the range mid on a double-break day (2026-07-10 11:05), a P-zone
    # reversal (2026-05-20 09:46), a Judas on a single-break day (2025-10-14), two
    # extension reactions after the eighth New York entry (2025-09-09, 2026-07-06)
    # and a second entry at a London quadrant (2025-10-07). Open, the list holds
    # 25 of his 30 tickets within ten points on the right bar against 0.23 for fake
    # tickets, at about 32 candidates a day (gated and capped: 20 of 30 against 0.07
    # at about 12). The play, the caps and the position rules shape the EXECUTED
    # list below. Both lists share the double-break clock rules that follow; "one thesis
    # per session" (the purged-day retest and the outbound taken once) is an execution
    # rule and leaves the candidates alone: his 2026-05-15 buys are the afternoon's tests
    # of lines the morning had already tested.
    if classification == "double_break":
        # "cycle 1 from 09:30 to the 09:40-09:50 window (the Judas), cycle 2 from
        # there to 12:00" (audit §1.1 clocks): the first hour belongs to the
        # Judas; the range scalps of the rotation play join from 10:00. The
        # pre-open EQ tag ("range mid provided the entry area", 2026-07-27
        # 09:02) is taken before the RTH open when the read supports it: the
        # open outside prior value on the purged side (07-27 opens above the
        # VAH with the overnight high purged, JR p.34) or a big 6-9 range
        # ("when having a big 6-9 range > long/short the EQ", JR p.3). On any
        # other read the tag fired on 16 replay days and stopped on 15.
        ten, open_ns = _at(market, "10:00"), _at(market, "09:30")
        passing = [ep for ep in passing if ep.get("branch") != "internal_rotation" or int(ep.get("decision_at") or 0) >= ten]
        branches.add("single_extended")
        tag_admitted = bool(read.get("aligned") or read.get("big_range"))
        pre_open_eq = [ep for ep in passing if tag_admitted and ep.get("branch") == "single_extended" and int(ep.get("decision_at") or 0) < open_ns and (ep.get("values") or {}).get("cycle") == 0]
        if pre_open_eq:
            first_side = min(pre_open_eq, key=lambda ep: int(ep.get("decision_at") or 0)).get("side")
            pre_open_eq = [ep for ep in pre_open_eq if ep.get("side") == first_side]
        passing = [ep for ep in passing if ep.get("branch") != "single_extended"] + pre_open_eq
    candidates_pool = list(passing)
    for one_shot in ("single_purged", "judas_outbound"):
        # "one thesis per session": the purged-day retest and the outbound are
        # taken once, at the first line that gives the entry (2026-07-28 09:35)
        group = [ep for ep in passing if ep.get("branch") == one_shot]
        if group:
            first = min(group, key=lambda ep: int(ep.get("decision_at") or 0))
            first_values = first.get("values") or {}
            keep = [
                ep for ep in group
                if (ep.get("values") or {}).get("reference_kind") == first_values.get("reference_kind")
                and (ep.get("values") or {}).get("cycle") == first_values.get("cycle")
                and ep.get("side") == first.get("side")
            ]
            passing = [ep for ep in passing if ep.get("branch") != one_shot] + keep
    # "scaling in at the lines and out at the next line" (audit 1.1): the
    # Judas is entered at the edge and added at the projection and internal
    # lines it reaches (2026-09-01 buys the -0.33 at 09:40 with the box low
    # taken at 09:30); an add is a fill of the open thesis and does not use a
    # round trip. A setup on the other side flips the position (2025-10-13).
    # The CANDIDATE list is the object he chooses from: every opportunity the
    # framework admits, once (user instruction 2026-09-17: the list is per
    # play and small, not a cap on a crowd). The EXECUTED list beside it is
    # one position at a time with his adds and flips.
    def segment(pool, clock, cap, open_candidates, trade_windows):
        if CANDIDATES_GATE_BY_PLAY:
            candidates = select_session_trades(pool, bars=bars, clock=clock, max_entries=cap, stop_after_target=False, edge_first=EDGE_FIRST, max_per_line=MAX_PER_LINE, one_position=False, reenter_same_line=CANDIDATES_REENTER_SAME_LINE)
        else:
            candidates = select_session_trades(open_candidates, bars=bars, clock=clock, max_entries=10**6, stop_after_target=False, edge_first=EDGE_FIRST, max_per_line=None, one_position=False, reenter_same_line=True)
        candidates["executed"] = select_session_trades(
            pool, bars=bars, clock=clock, max_entries=cap, stop_after_target=trade_windows is not None, edge_first=EDGE_FIRST, allow_adds=EXECUTED_ALLOW_ADDS,
            max_per_line=MAX_PER_LINE, allow_flips=EXECUTED_ALLOW_FLIPS,
            windows=None if trade_windows is None else [(_at(market, a), _at(market, b), n) for a, b, n in trade_windows],
        )
        return candidates
    london = segment([ep for ep in passing if ep.get("branch") == "other_session"], (_at(market, SEGMENTS["london"][0]), _at(market, SEGMENTS["london"][1])), LONDON_ROUND_TRIPS, [ep for ep in candidates_pool if ep.get("branch") == "other_session"], LONDON_TRADE_WINDOWS)
    ny = segment([ep for ep in passing if ep.get("branch") in branches], (_at(market, SEGMENTS["ny"][0]), _at(market, SEGMENTS["ny"][1])), NY_ROUND_TRIPS, [ep for ep in candidates_pool if ep.get("branch") != "other_session"], NY_TRADE_WINDOWS)
    entries = list(london.get("entries") or []) + list(ny.get("entries") or [])
    entries.sort(key=lambda row: int(row.get("decision_at") or 0))
    executed = list(london["executed"].get("entries") or []) + list(ny["executed"].get("entries") or [])
    executed.sort(key=lambda row: int(row.get("decision_at") or 0))
    return {
        "entries": entries,
        "n_entries": len(entries),
        "executed": {"entries": executed, "n_entries": len(executed), "n_round_trips": int(london["executed"].get("n_round_trips") or 0) + int(ny["executed"].get("n_round_trips") or 0)},
        "n_candidates": int(london.get("n_candidates") or 0) + int(ny.get("n_candidates") or 0),
        "segments": {"london": london, "ny": ny},
        "primary_play": primary_play or read.get("primary_play"),
        "classification": classification,
        "branches": sorted(branches),
        "fallback_play_used": False,
        "mode_preference_fallback": sorted(set(london.get("mode_preference_fallback") or []) | set(ny.get("mode_preference_fallback") or [])),
    }


def scan_b02(market, rec, *, overrides=None) -> dict[str, Any]:
    """Source-faithful B0.3 scan. Does not mutate B0 or B0.1 documents."""
    with enumeration_scope(overrides):
        return _scan_b02_impl(market, rec, overrides=overrides)


def _scan_b02_impl(market, rec, *, overrides=None) -> dict[str, Any]:
    stage_overrides, _enum = split_b02_overrides(overrides)

    def finish(doc):
        if not stage_overrides:
            return doc
        from trading_research.research.rule_discovery.search import finish_scan_b02

        return finish_scan_b02(doc, stage_overrides)

    day = _as_day(market) if market is not None else None
    branch = _rec_branch(rec)
    if market is None or day is None:
        return finish(_document(market, branch or "all", [], [{"reason": "data_unavailable"}]))
    if not is_native_session(day):
        return finish(_document(market, branch or "all", [], [{"reason": "data_unavailable", "date": day.isoformat()}]))
    branches = BRANCHES if not branch or branch in {"*", "all", "B0.2", "B0.3"} else (branch,)
    context = session_context(market)
    read = context.get("read") or {}
    episodes: list[dict[str, Any]] = []
    omissions: list[dict[str, Any]] = []
    for item in branches:
        scanner = _SCANNERS.get(item)
        if scanner is None:
            omissions.append({"reason": "unknown_branch", "branch": item})
            continue
        try:
            part, omit = scanner(market)
        except Exception as exc:
            omissions.append({"reason": "scan_error", "branch": item, "error": f"{type(exc).__name__}: {exc}"})
            continue
        episodes.extend(part)
        omissions.extend(omit)
    episodes = list(enumeration_point("contacts", episodes, market=market, family=FAMILY) or episodes)
    for episode in episodes:
        play = PLAY_OF_BRANCH.get(episode.get("branch"))
        episode["values"]["play"] = play
        episode["values"]["is_primary_play"] = play == read.get("primary_play")
    selection = selection_for(market, episodes, primary_play=read.get("primary_play"))
    label = branch if branch and branch not in {"*", "all", "B0.2", "B0.3"} else "all"
    return finish(_document(market, label, episodes, omissions, selection=selection, day_read=read))



RULES = {
    "JJ-CONFIRM-two-minute-grid": {
        "kind": "literal",
        "source": "audit 1.1 'Confirmation' (the 2/3/5-minute clocks); JR p.42, 2026-07-10 buy 29,809 at 11:05 -- the fixed-grid 11:00-11:02 candle closes 29,808.00",
        "finding": "J-B",
        "parameters": {"clock_seconds": 120, "grid_origin": "09:00", "fill": "the candle's close"},
        "note": "round 3: the candle is the one on the chart's fixed two-minute grid, not a two-minute window re-anchored to the touch",
        "_fn": _two_minute_reclaim,
    },
    "JJ-LOC-prior-rth-value": {
        "kind": "literal",
        "source": "JR p.42 'after the test of pRTHVAL / R-Lo' (pRTHVAL 29,790, R-Lo 29,770); the MGLevels panel draws pRTHVAH / pRTHVAL / POC",
        "finding": "J-C",
        "parameters": {"levels": ["prth_vah", "prth_val", "prth_poc"], "play": "internal_rotation"},
        "_fn": _eq_lines,
    },
    "JJ-FILL-limit-at-the-line": {
        "kind": "literal",
        "source": "JR p.42 (the 11:05 quadrant fill) and p.41 (the EQ rejection); the author rests a limit at each drawn line the move reaches",
        "finding": "J-A",
        "parameters": {"lines": ["eq", "q25", "q75", "range_open", "or15_*", "prth_*"], "fill_time": "the touch, after the evidence that placed the order"},
        "note": "round 3: a resting limit is filled when price touches it, never before the evidence that put it there",
        "_fn": _fill_modes,
    },
    "JJ-OUTBOUND-geometry": {
        "kind": "literal",
        "source": "audit 1.1 'Trade #1'; coordinator J-E 2026-09-17: the opening drive takes a drawn level and the trade runs with the break to the +/-0.5 projection",
        "finding": "J-E",
        "parameters": {
            "fill": "the first box internal beyond the broken level, in the break direction",
            "stop": "back on the far side of the broken level",
            "objective": "the opposite edge plus the half projection",
            "expiry": MODAL_WINDOW[0],
        },
        "note": "round 3: the internal filter and the stop were both on the wrong side, so this branch passed 0 of 8,313 episodes",
        "_fn": _scan_judas_outbound,
    },
    "JJ-BOX-06-09-and-ladder": {
        "kind": "literal",
        "source": "audit 1.1; JR pp.16-18, 71; charts 2025-01-28, 2025-10-01, 2025-10-14",
        "finding": "RR-06",
        "parameters": {
            "ny_box": "06:00-09:00 ET frozen at 09:00",
            "london_box": "02:00-03:00 traded 03:00-06:00",
            "internals": ["HIGH", "LOW", "EQ", "25%", "75%", "range open", "range close"],
            "ladder": [str(item) for item in LADDER_MULT],
        },
    },
    "JJ-CLASSIFIER-range-size-and-open-location": {
        "kind": "literal",
        "source": "audit 1.1; the author's 2026-06-08 table over 3,249 days and the 2026-07-28 open-location table",
        "finding": "J9",
        "parameters": {"bins": [row[0] for row in RANGE_BINS], "single_break_from": str(SINGLE_BREAK_MIN_BIN)},
    },
    "JJ-CONFIRM-from-0900": {
        "kind": "literal",
        "source": "audit 1.3 J2; JR p.20 (09:03), 2026-01-09 (09:32), 2026-02-24 (09:33), 2026-08-28 (09:30-09:32)",
        "finding": "J2",
        "parameters": {"from": "the sweep end, at or after 09:00", "modal_window": list(MODAL_WINDOW), "modal_is_operand": True},
    },
    "JJ-CONFIRM-any-2m-3m-5m-ob-rb-absorption": {
        "kind": "literal",
        "source": "TBR pp.27-29, p.35; audit 1.3 J7",
        "finding": "J7",
        "parameters": {"timeframes": [2, 3, 5], "signatures": ["orderblock", "rejection_block", "absorption"]},
    },
    "JJ-LOCATIONS-any-drawn-level": {
        "kind": "literal",
        "source": "audit 1.3 J4",
        "finding": "J4",
        "parameters": {"kinds": ["box edges", "London H/L", "Asia H/L", "D-1..D-3 H/L", "ONH/ONL", "pRTHVAH/pRTHVAL"]},
    },
    "JJ-LOCATION-exhaustion-area": {
        "kind": "literal",
        "source": "audit 1.1/1.3 J5: the sweep extends to the exhaustion area (0.33-0.66 band, 0.5, a P-zone, an overnight or London/Asia extreme)",
        "finding": "J5",
        "parameters": {"depth_classes": list(DEPTH_CLASSES), "coincidence_points": str(LEVEL_COINCIDENCE)},
    },
    "JJ-OBJECTIVE-ladder": {
        "kind": "literal",
        "source": "audit 1.3 J1; the author's 2026-01-02 retrace table (EQ 92.8 / range open 86.8 / opposite edge 66.2)",
        "finding": "J1",
        "parameters": {"ladder": ["eq", "range_open", "opposite_edge", "half_projection", "extension_band"]},
    },
    "JJ-LONDON-no-edge-raid-required": {
        "kind": "literal",
        "source": "audit 1.3 J8; London charts 2025-10-07 and 2025-10-08 (entry at the 25% line, no edge sweep)",
        "finding": "J8",
    },
    "JJ-SINGLE-PURGED-am-window-and-projection-objective": {
        "kind": "literal",
        "source": "audit 1.3 J10/J11/J12",
        "finding": "J11",
        "parameters": {"window": "09:00-12:00", "add_window": list(MODAL_WINDOW), "objective": "the -1 / -1.33 / -1.66 projections"},
    },
    "JJ-SINGLE-EXTENDED-out-by-1000": {
        "kind": "literal",
        "source": "audit 1.3 J9; TBR p.12",
        "finding": "J9",
        "parameters": {"entry_window": "09:00-10:30", "objective": "the range edges"},
    },
    "JJ-OR15-retracement": {
        "kind": "literal",
        "source": "audit 1.3 J3; 2026-02-24, 2026-07-16, 2026-07-21 OR-mid retracements",
        "finding": "J3",
        "parameters": {"locations": ["or15_mid", "or15_q25", "or15_q75"], "sibling_of": "the single-break case"},
    },
    "JJ-SESSIONSTAT-computed": {
        "kind": "literal",
        "source": "audit 1.3 J13; SessionStat+ manual; readouts 2025-05-23, 2025-09-09, 2026-07-06",
        "finding": "J13",
        "parameters": {"sample": SESSIONSTAT_SAMPLE, "measure": "mean and median high/low excursion from the session open"},
    },
    "JJ-EXTENSION-after-1000": {
        "kind": "literal",
        "source": "JR pp.25-26; audit 1.2 extension_reaction is faithful",
        "finding": "RR-03",
        "parameters": {"band": [str(EXTENSION_BAND[0]), str(EXTENSION_BAND[1])], "window": list(NY_EXTENSION_ACTION)},
    },
    "JJ-PZONE-unsupported-input": {
        "kind": "OD",
        "source": "audit 1.2: the P-zone generator is proprietary; only the six printed dates exist",
        "finding": "F17",
    },
    "JJ-EVRANGE-unsupported-input": {
        "kind": "OD",
        "source": "audit 1.2: EVRange is proprietary; the two printed readouts are fixtures",
        "finding": "F17",
        "parameters": {"fixtures": sorted(EVRANGE_FIXTURES)},
    },
    "JJ-SELECT-one-thesis-a-session": {
        "kind": "literal",
        "source": "audit 1.1 'Sizing and frequency': one thesis per session, one to four round trips",
        "finding": "J-frequency",
        "parameters": {"max_entries": MAX_ENTRIES_PER_SESSION},
    },
    "JJ-CLOCKS-ET": {"kind": "literal", "source": "TBR p.6; JR p.71 ticket UTC; 2026 NT charts UK local", "finding": "F18"},
    "JJ-BIGTRADES-deferred": {
        "kind": "OD",
        "source": "JR p.50 BigTrades NQ >=100 NY / >=75 London; the series is not on the native tape",
        "finding": "RR-09",
        "status": "deferred",
    },
}

_RULES_CACHE: list[dict[str, Any]] | None = None


def rules_payload() -> list[dict[str, Any]]:
    global _RULES_CACHE
    if _RULES_CACHE is not None:
        return _RULES_CACHE
    impl = {
        "JJ-BOX-06-09-and-ladder": box_geometry,
        "JJ-CLASSIFIER-range-size-and-open-location": range_class,
        "JJ-CONFIRM-from-0900": _scan_judas_reversal,
        "JJ-CONFIRM-any-2m-3m-5m-ob-rb-absorption": confirm_pack,
        "JJ-LOCATIONS-any-drawn-level": drawn_levels,
        "JJ-LOCATION-exhaustion-area": exhaustion_hit,
        "JJ-OBJECTIVE-ladder": objective_ladder,
        "JJ-LONDON-no-edge-raid-required": _scan_other_session,
        "JJ-SINGLE-PURGED-am-window-and-projection-objective": _scan_eq_branch,
        "JJ-SINGLE-EXTENDED-out-by-1000": _scan_eq_branch,
        "JJ-OR15-retracement": _eq_lines,
        "JJ-SESSIONSTAT-computed": sessionstat_envelope,
        "JJ-EXTENSION-after-1000": _scan_extension_reaction,
        "JJ-PZONE-unsupported-input": _scan_pzone,
        "JJ-SELECT-one-thesis-a-session": select_session_trades,
    }
    rows = []
    for rule_id, meta in RULES.items():
        fn = impl.get(rule_id)
        try:
            line = f"source_adapters/jumbo.py:{inspect.getsourcelines(fn)[1]}" if fn is not None else "source_adapters/jumbo.py"
        except (OSError, TypeError):
            line = "source_adapters/jumbo.py"
        rows.append({"rule_id": rule_id, "kind": meta["kind"], "source": meta["source"], "finding": meta.get("finding"), "file_line": line, **({"parameters": meta["parameters"]} if "parameters" in meta else {})})
    _RULES_CACHE = rows
    return rows


def funnel_stage_counts(episodes: list[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    """Cascade pass along STAGE_ORDER. A fail stops later pass counts."""
    if not episodes:
        return {}
    counts = {name: {"pass": 0, "fail": 0, "unknown": 0} for name in STAGE_ORDER}
    for episode in episodes:
        by_name = {str(row.get("stage")): row for row in episode.get("stages") or []}
        alive = True
        for name in STAGE_ORDER:
            row = by_name.get(name)
            if row is None or not alive:
                continue
            verdict = str(row.get("verdict") or "unknown")
            counts[name][verdict] = counts[name].get(verdict, 0) + 1
            if verdict == "fail":
                alive = False
    return {name: counts[name] for name in STAGE_ORDER if any(counts[name].values())}


def classify_first_hour_sweep(took_h: bool, took_l: bool) -> dict[str, int]:
    """JR p.37: one_side is high_only + low_only. both is a separate bucket."""
    row = {"high_only": 0, "low_only": 0, "both": 0, "one_side": 0}
    if took_h and took_l:
        row["both"] = 1
    elif took_h:
        row["high_only"] = 1
        row["one_side"] = 1
    elif took_l:
        row["low_only"] = 1
        row["one_side"] = 1
    return row


# ---------------------------------------------------------------------------
# author-example replay (entries only, user instruction 2026-09-17)


def proper_entries(example: Mapping[str, Any]) -> list[dict[str, Any]]:
    out = []
    for row in example.get("actions") or []:
        if not isinstance(row, Mapping) or not row.get("proper_entry"):
            continue
        action = str(row.get("action") or "")
        side = row.get("side") or ("long" if action == "buy" else "short" if action == "sell" else None)
        out.append(
            {
                "time_et": row.get("time_et"),
                "date": row.get("date") or example.get("date"),
                "side": side,
                "price": _d(row.get("price")),
                "reference_price": _d(row.get("reference_price")),
                "stop": _d(row.get("stop")),
                "target": _d(row.get("target")),
                "branch": row.get("branch"),
                "reference": row.get("reference"),
                "marked_by": row.get("marked_by"),
                "scored_by_decision": row.get("scored_by_decision"),
                "author_documented_mistake": row.get("author_documented_mistake"),
                "chart_clock": example.get("chart_clock"),
                "accepted_by_owner": row.get("accepted_by_owner"),
            }
        )
    return out


def other_fills(example: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"time_et": row.get("time_et"), "action": row.get("action"), "price": row.get("price"), "note": row.get("note")}
        for row in example.get("actions") or []
        if isinstance(row, Mapping) and row.get("price") is not None and not row.get("proper_entry")
    ]


def _entry_ns(market, date_text, time_et) -> int | None:
    if not time_et:
        return None
    token = str(time_et).split("-")[0].split("(")[0].strip()
    parts = token.split(":")
    if len(parts) < 2:
        return None
    try:
        hour, minute = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    session_day = _as_day(market)
    day = session_day
    dated = False
    if date_text:
        try:
            day = date.fromisoformat(str(date_text)[:10])
            dated = True
        except ValueError:
            day = session_day
    offset = (day - session_day).days
    # An evening stamp belongs to the session that OPENS that evening. When the
    # example carries its own calendar date that is already in the offset above;
    # shifting again put the stamp a full day before its session.
    if hour >= 18 and not dated:
        offset -= 1
    try:
        return int(_at(market, f"{hour:02d}:{minute:02d}", offset))
    except Exception:
        return None


def _bars_from_window(at_ns: int, window: tuple[int, int]) -> float:
    """Distance from the printed window, in five-minute bars; zero inside it."""
    if window[0] <= at_ns <= window[1]:
        return 0.0
    gap = window[0] - at_ns if at_ns < window[0] else at_ns - window[1]
    return gap / FIVE


def _printed_window_ns(market, date_text, time_et) -> tuple[int, int] | None:
    """The printed entry time, or the printed window when the post gives a range.

    Charts are read to the minute the author drew, and several posts print a
    window ("09:40-09:50", "03:00-04:00") rather than a fill time. The window is
    the acceptance band; a single stamp is the stamp.
    """
    if not time_et:
        return None
    text = str(time_et)
    first = _entry_ns(market, date_text, text)
    if first is None:
        return None
    tail = text.split("-", 1)[1].strip() if "-" in text else None
    last = _entry_ns(market, date_text, tail) if tail else None
    if last is None or last < first:
        last = first
    return first, last


def _printed_window_for(market, entry: Mapping[str, Any]) -> tuple[int, int] | None:
    """The printed window, shifted for charts that label bars by their close.

    NinjaTrader labels a bar with the time it ENDS, so a fill the author marks
    at 09:35 traded inside the bar that opens 09:34. TradingView labels bars by
    their open and needs no shift. Without this the NinjaTrader examples are
    read one minute late and every match is pushed a bar out.
    """
    window = _printed_window_ns(market, entry.get("date"), entry.get("time_et"))
    if window is None:
        return None
    clock_text = str(entry.get("chart_clock") or "").lower()
    if "ninjatrader" in clock_text:
        shift = 60 * 1_000_000_000
        return window[0] - shift, window[1] - shift
    return window


#: Owner decision, 2026-09-17: the fill tolerance for a reproduced entry.
STRICT_10_POINTS = Decimal("10")


def _mode_supported(branch: str | None, mode: str | None) -> bool:
    """Is this fill mode one the source or the tickets support for this branch?

    ``MODE_PREFERENCE`` is the order read off the author's own tickets. Where a
    branch has an order, only those modes count; where the tickets are silent
    the branch has no order and every mode the scanner emits is admissible --
    silence is not evidence against a mode.
    """
    order = MODE_PREFERENCE.get(str(branch)) or ()
    if not order:
        return True
    return str(mode) in order


def _expected_play(entry: Mapping[str, Any]) -> str | None:
    """The play of the record's primary branch (the first of its alternatives)."""
    for branch in branch_alternatives(entry.get("branch")):
        play = PLAY_OF_BRANCH.get(branch)
        if play is not None:
            return play
    return None


def _expected_plays(entry: Mapping[str, Any]) -> set[str]:
    return {PLAY_OF_BRANCH[branch] for branch in branch_alternatives(entry.get("branch")) if branch in PLAY_OF_BRANCH}


def match_entry(market, episodes, entry, *, strict_points: Decimal | None = None) -> dict[str, Any]:
    """Does any episode produce this narrated entry, on this side, at this time?

    Where the post prints a fill the comparison is entry price to fill price.
    Where the post narrates the trade without printing a fill, the comparison is
    our reference level to the level the post names.
    """
    if strict_points is None:
        strict_points = REPLAY_LEVEL_TOLERANCE  # read at call time so a rescan override reaches it
    window = _printed_window_for(market, entry)
    want_ns = None if window is None else window[0]
    price = entry.get("price")
    compare_to = price if price is not None else entry.get("reference_price")
    compare_field = "entry" if price is not None else "reference_level"
    side = entry.get("side")
    risk = None
    if price is not None and entry.get("stop") is not None:
        risk = abs(entry["stop"] - price)
    tolerance = risk if risk is not None else TICKET_RISK_FALLBACK
    rows = []
    want_plays = _expected_plays(entry)
    for ep in episodes:
        if ep.get("research_verdict") != "pass" or ep.get("side") != side:
            continue
        if want_plays and PLAY_OF_BRANCH.get(ep.get("branch")) not in want_plays:
            continue
        geometry = ep.get("geometry") or {}
        got = _d(geometry.get("entry")) if compare_field == "entry" else _d(geometry.get("reference_level"))
        at_ns = ep.get("decision_at")
        if got is None or at_ns is None:
            continue
        rows.append(
            {
                "episode": ep,
                "value": got,
                "at_ns": int(at_ns),
                "delta_points": None if compare_to is None else abs(got - compare_to),
                "bars_from_printed": None if window is None else _bars_from_window(int(at_ns), window),
                "branch": ep.get("branch"),
                "reference_kind": (ep.get("values") or {}).get("reference_kind"),
                "mode": (ep.get("values") or {}).get("confirmation_mode"),
            }
        )
    # R2 (coordinator round 2): a ticket time is a stamp and keeps one
    # five-minute bar; a time read off a chart is a chart read and gets three.
    bars_allowed = 1.0 if entry.get("marked_by") == "rr_tool" else 3.0
    in_time = [row for row in rows if row["bars_from_printed"] is not None and row["bars_from_printed"] <= bars_allowed]
    want_branches = set(branch_alternatives(entry.get("branch")))
    if in_time:
        scored = sorted(
            in_time,
            key=lambda row: (
                0 if want_branches and row["branch"] in want_branches else 1,
                Decimal("1e9") if row["delta_points"] is None else row["delta_points"],
            ),
        )
    else:
        scored = sorted(
            rows,
            key=lambda row: (
                9e9 if row["bars_from_printed"] is None else row["bars_from_printed"],
                0 if want_branches and row["branch"] in want_branches else 1,
            ),
        )
    best = scored[0] if scored else None
    ok_time = best is not None and best["bars_from_printed"] is not None and best["bars_from_printed"] <= bars_allowed
    # The owner's rule: strict wherever a PRICE is printed, play + side + time
    # where the ticket prints none. A narrated reference level is still compared
    # and reported (``delta_points`` against ``compare_to``), but it is a
    # diagnostic -- it is not a fill, so it cannot make or break a strict match.
    no_price = price is None
    accepted = entry.get("accepted_by_owner")
    # Owner decision, 2026-09-17: an entry counts as reproduced when the fill is
    # within TEN points of the printed price on the right bar AND follows the
    # author's framework -- same play, same branch, same side, and a fill mode
    # the source or the tickets support. A coincidental fill from another branch
    # or an unsupported mode inside ten points is NOT a match. The old +/-5
    # count is kept beside it so the change stays visible.
    framework = [
        row
        for row in rows
        if row["branch"] in want_branches and _mode_supported(row["branch"], row["mode"])
    ]
    framework_in_time = [
        row for row in framework if row["bars_from_printed"] is not None and row["bars_from_printed"] <= bars_allowed
    ]
    framework_best = min(
        framework_in_time,
        key=lambda row: Decimal("1e9") if row["delta_points"] is None else row["delta_points"],
        default=None,
    )

    def _framework_hit(points: Decimal) -> bool:
        if framework_best is None:
            return False
        if no_price:
            return True
        return framework_best["delta_points"] is not None and framework_best["delta_points"] <= points
    return {
        "printed_time_et": entry.get("time_et"),
        "printed_price": None if price is None else float(price),
        "printed_reference": None if entry.get("reference_price") is None else float(entry["reference_price"]),
        "compare_field": compare_field,
        "printed_side": side,
        "printed_stop": None if entry.get("stop") is None else float(entry["stop"]),
        "marked_by": entry.get("marked_by"),
        "expected_branch": entry.get("branch"),
        "tolerance_points": float(tolerance),
        "strict_points": float(strict_points),
        "no_printed_level": no_price,
        "detected": bool(
            best
            and ok_time
            and (no_price or (best["delta_points"] is not None and best["delta_points"] <= tolerance))
            and PLAY_OF_BRANCH.get(best["branch"]) in _expected_plays(entry)
        ),
        # R3 rule A: where the ticket prints no price the match is play + side +
        # time; there is no price to be strict about, so the strict column is
        # the same test as the detected column rather than an automatic miss.
        "accepted_by_owner": accepted,
        "framework_entry": None if framework_best is None else float(framework_best["value"]),
        "framework_delta_points": None if framework_best is None or framework_best["delta_points"] is None else float(framework_best["delta_points"]),
        "framework_bars": None if framework_best is None else framework_best["bars_from_printed"],
        "framework_mode": None if framework_best is None else framework_best["mode"],
        "detected_strict_10": _framework_hit(STRICT_10_POINTS),
        "detected_strict": _framework_hit(strict_points),
        "detected_within_3_bars": bool(
            best
            and best["bars_from_printed"] is not None
            and best["bars_from_printed"] <= 3.0
            and (no_price or (best["delta_points"] is not None and best["delta_points"] <= tolerance))
            and PLAY_OF_BRANCH.get(best["branch"]) in _expected_plays(entry)
        ),
        "our_entry": None if best is None else float(best["value"]),
        "our_entry_ns": None if best is None else best["at_ns"],
        "our_branch": None if best is None else best["branch"],
        "our_mode": None if best is None else best["mode"],
        "our_reference": None if best is None else best["reference_kind"],
        "our_play": None if best is None else PLAY_OF_BRANCH.get(best["branch"]),
        "expected_play": _expected_play(entry),
        "play_matches": None if best is None else PLAY_OF_BRANCH.get(best["branch"]) in _expected_plays(entry),
        "delta_points": None if best is None or best["delta_points"] is None else float(best["delta_points"]),
        "bars_from_printed": None if best is None or best["bars_from_printed"] is None else float(best["bars_from_printed"]),
        "n_pass_episodes": len(rows),
        "bars_allowed": bars_allowed,
        "fills_tested": sorted({str(row["mode"]) for row in rows}),
        "matched_fill": None if best is None else best["mode"],
    }


def replay_example(market, example) -> dict[str, Any]:
    example = dict(example or {})
    day_text = example.get("date")
    day = date.fromisoformat(str(day_text)[:10]) if day_text else (_as_day(market) if market is not None else None)
    if example.get("inside_tape") is False or (day is not None and not is_native_session(day)):
        return {
            "example_id": example.get("id"),
            "detected": None,
            "divergence": OUTSIDE_TAPE,
            "entries": [],
            "other_fills": other_fills(example),
            "branch": None,
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": None,
            "author_side": None,
            "reached_location": None,
            "failing_stage": None,
            "failing_operand": "date",
        }
    document = scan_b02(market, {"branch": "all"})
    episodes = document.get("episodes") or []
    read = document.get("day_read") or {}
    entries = proper_entries(example)
    matched = [match_entry(market, episodes, entry) for entry in entries]
    detected = None if not matched else all(row["detected"] for row in matched)
    best = next((row for row in matched if row["detected"]), matched[0] if matched else None)
    return {
        "example_id": example.get("id"),
        "detected": detected,
        "detected_strict": None if not matched else all(row["detected_strict"] for row in matched),
        "entries": matched,
        "n_proper_entries": len(matched),
        "n_detected": sum(1 for row in matched if row["detected"]),
        "other_fills": other_fills(example),
        "day_read": read,
        "play": None if best is None else best.get("our_play"),
        "expected_play": None if not matched else matched[0].get("expected_play"),
        "branch": None if best is None else best["our_branch"],
        "our_side": None if not entries else entries[0].get("side"),
        "our_level": None if best is None else best["our_entry"],
        "our_entry_ns": None if best is None else best["our_entry_ns"],
        "author_level": None if best is None else (best["printed_price"] if best["printed_price"] is not None else best["printed_reference"]),
        "author_side": None if not entries else entries[0].get("side"),
        "reached_location": bool(episodes),
        "failing_stage": None if detected else "confirmation",
        "failing_operand": None if detected else "entry_price_or_time",
        "divergence": "" if detected else "entry_not_reproduced",
    }


def compute_published_statistics(dates: list[str]) -> dict[str, Any]:
    """The author's published numbers, for the plausibility section to reproduce."""
    return {
        "extended_range_reversal_share": 0.8646,
        "reversal_modal_window": "09:40-09:50",
        "average_reversal_time_original": "09:47:36",
        "average_reversal_time_extended": "09:51:05",
        "break_classification_all_days": {"double": 0.448, "single_high": 0.280, "single_low": 0.261, "none": 0.011},
        "retrace_after_low_sweep": {
            "09:00-10:00": {"eq": 0.928, "range_open": 0.868, "range_high": 0.662},
            "10:00-11:00": {"eq": 0.855, "range_open": 0.763, "range_high": 0.515},
            "11:00-12:00": {"eq": 0.752, "range_open": 0.623, "range_high": 0.354},
        },
        "dates": list(dates),
        "source": "JR pp.23, 37, 70; the author's 2026-01-02 and 2026-06-08 tables",
    }
