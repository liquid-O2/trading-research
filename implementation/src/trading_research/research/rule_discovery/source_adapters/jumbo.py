"""P15-09 Jumbo range branches."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping
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
    return int(market.at("09:40"))


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
        deadline = min(deadline, int(market.at("09:50")))
    if branch == "judas_outbound":
        openbars = market.bars(market.at("09:30"), market.at("09:30") + 1_000_000_000, 1)
        from trading_research.research.method_pack.historical_flow import batches

        opening = batches(market.local(market.at("09:30"), market.at("09:30") + 1_000_000_000))
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
    context_at = int(market.at("09:30"))
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
        values["at_rth_open"] = first is not None and market.at("09:30") <= first[0] < market.at("09:30") + 1_000_000_000
        values["objective_is_selected_exhaustion"] = True if width is not None else None
        values["exit_window_recorded"] = True
    elif branch in {"judas_reversal", "judas_reversal_deferred"}:
        swept = None
        if edge is not None and trigger.get("L") is not None:
            swept = trigger["L"] < edge if side == "long" else trigger["H"] > edge
        values["reversal_context"] = None if pw is None else (width is not None and width > 0)
        values["edge_swept"] = swept
        values["sweep_at"] = touch
        values["source_time_window"] = market.at("09:30") <= int(touch) < market.at("09:50")
        values["objective_is_opposing_draw"] = True if target is not None else None
        values["entry_in_reversal_window"] = market.at("09:40") <= int(decision) < market.at("09:50")
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
    MAX_ENTRIES_PER_SESSION,
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
    try:
        return int(market.at(hhmm, offset))
    except TypeError:
        return int(market.at(hhmm))


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
    if kind == "ny":
        start, end = _at(market, "06:00"), _at(market, "09:00")
    elif kind == "london":
        start, end = _at(market, LONDON_BOX_WINDOW[0]), _at(market, LONDON_BOX_WINDOW[1])
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


def drawn_levels(market, box: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """J4: every drawn liquidity level the author sweeps, not only R-Hi/R-Lo.

    "The author sweeps any drawn liquidity level (London high on 2026-07-16 at
    29,530 inside the box, D-1/D-2 highs on 2026-01-02 and 2026-08-28, the
    pre-market swing high on 2025-10-03, the prior RTH high)."
    """
    out: list[dict[str, Any]] = []

    def add(kind: str, side: str, price: Decimal | None, known_at: int) -> None:
        if price is None:
            return
        out.append({"kind": kind, "side": side, "price": price, "known_at": int(known_at)})

    if box is not None:
        add("box_low", "long", box["low"], box["known_at"])
        add("box_high", "short", box["high"], box["known_at"])
    london = box_geometry(market, "london")
    if london is not None:
        add("london_low", "long", london["low"], london["known_at"])
        add("london_high", "short", london["high"], london["known_at"])
    asia = _span(_bars(market, _at(market, "20:00", -1), _at(market, "00:00"), 60), known_at=_at(market, "00:00"))
    if asia is not None:
        add("asia_low", "long", asia["low"], asia["known_at"])
        add("asia_high", "short", asia["high"], asia["known_at"])
    overnight = _span(_bars(market, _at(market, "18:00", -1), _at(market, "09:00"), 60), known_at=_at(market, "09:00"))
    if overnight is not None:
        add("onl", "long", overnight["low"], overnight["known_at"])
        add("onh", "short", overnight["high"], overnight["known_at"])
    for index, span in enumerate(prior_sessions(market, 3), start=1):
        add(f"d{index}_low", "long", span["low"], span["known_at"])
        add(f"d{index}_high", "short", span["high"], span["known_at"])
    value = prior_value_area(market)
    if value:
        add("prth_val", "long", value.get("val"), value.get("known_at") or market.start)
        add("prth_vah", "short", value.get("vah"), value.get("known_at") or market.start)
    # J-F: the London session's own references are the Asia high/low, the
    # midnight 00:00-00:30 range and the overnight extremes, all drawn before
    # 02:00 (2025-05-23 buys the prior RTH low at 02:20).
    try:
        prior_rth = (market.prior("day") or {}).get("range")
    except Exception:
        prior_rth = None
    if prior_rth and prior_rth.get("low") is not None:
        add("prth_low", "long", _d(prior_rth["low"]), int(prior_rth.get("known_at") or market.start))
        add("prth_high", "short", _d(prior_rth["high"]), int(prior_rth.get("known_at") or market.start))
    midnight = _span(_bars(market, _at(market, "00:00"), _at(market, "00:30"), 60), known_at=_at(market, "00:30"))
    if midnight is not None:
        add("midnight_low", "long", midnight["low"], midnight["known_at"])
        add("midnight_high", "short", midnight["high"], midnight["known_at"])
    return out


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
        "case": "double_break_favoured" if size["single_break_favoured"] is False else "single_break_favoured",
        "levels": drawn_levels(market, box),
        "evrange": EVRANGE_FIXTURES.get(str(market.day)),
        "pzones": PZONE_FIXTURES.get(str(market.day)) or [],
        "sessionstat": sessionstat_envelope(market),
    }
    context["read"] = session_read(market, context)
    setattr(market, "_jj_context", context)
    return context


# The play changes with the day (user instruction 2026-09-17). Each branch is
# one play; the day's classification decides which plays run at all.
PLAY_OF_BRANCH = {
    "judas_reversal": "double_break",
    "judas_outbound": "double_break",
    "extension_reaction": "double_break",
    "single_extended": "single_break",
    "single_purged": "single_break",
    "internal_rotation": "big_range_eq",
    "other_session": "london",
    "timed_pzone_reversal": "pzone",
}
# The author's own break-classification table (2026-06-08, 3,249 days, 9-12
# window) read by its modal category: double break leads every bin up to 1.2%
# (55.5 / 48.1 / 34.8 / 34.0) and only above 1.2% does a single break lead
# (single-low 38.5 against double 17.8).
DOUBLE_BREAK_MAX_PCT = Decimal("1.2")
# "same framework when having a big 6-9 range > long/short the EQ" (2026-09-02).
BIG_RANGE_MIN_PCT = Decimal("0.8")
OUTSIDE_VALUE = {"below_pdl", "below_val", "above_vah", "above_pdh"}


def _plays_for(location, pct, purge, *, pzone: bool) -> tuple[str, list[str]]:
    """The plays one open-location read admits, and the case it classifies."""
    aligned = (location in {"above_vah", "above_pdh"} and purge.get("purged_high") is True) or (
        location in {"below_val", "below_pdl"} and purge.get("purged_low") is True
    )
    decisive_trend = bool(aligned and pct is not None and pct >= DOUBLE_BREAK_MAX_PCT)
    if pct is None or location is None:
        return "unknown", ["london"]
    classification = "single_break" if aligned else "double_break"
    # J-C: the plays are observed, not switched by a threshold. Every play the
    # author runs is available every day; the classification chooses which is
    # primary and is what the frequency report is read against. The single-break
    # branches then gate themselves on the break state they actually observe and
    # the EQ play runs on every day as a lower-priority play.
    plays = ["london", "double_break", "single_break", "big_range_eq"]
    if pzone:
        plays.append("pzone")
    return classification, plays


def session_read(market, context: Mapping[str, Any]) -> dict[str, Any]:
    """The day's read, and the plays it allows, on the author's two clocks.

    Audit 1.1 "The classifier (decided before the open)": range size in percent
    of price, balanced versus already-purged overnight, the RTH open location
    against the prior RTH value area and range, which Asia/London/midnight
    edges still exist, sister-index relative strength and the news calendar.
    The last two are not on the owned tape and are recorded as unavailable
    rather than approximated.

    The author reads the location twice: once when the 06:00-09:00 box freezes
    at 09:00 and again at the RTH open, and his own posts quote the second
    ("open inside prior RTH value: range scalps", 2026-07-10; "RTH open below
    the prior RTH value low", 2026-07-28). Both reads are kept: the 09:00 read
    governs an entry taken before 09:30 and the 09:30 read governs the rest, so
    nothing is admitted on an input the scan could not yet see.

    The plays: a double-break / Judas day trades the 0.33/0.66 band, 0.5 and,
    after 10:00, the 1.33/1.66 band; a single-break / trend day trades the range
    OPEN, the EQ and the quadrants; a big 6-9 range is traded at the EQ.
    "Discard mean reversion and range double breaks when these things align"
    (2026-07-28) is the rule that switches the day off the Judas play.
    """
    size = context.get("range_class") or {}
    pct = size.get("pct")
    purge = context.get("purge") or {}
    pzone = bool(PZONE_FIXTURES.get(str(market.day)))
    pre_location = context.get("open_location")
    post_location = context.get("rth_open_location") or pre_location
    pre_class, pre_plays = _plays_for(pre_location, pct, purge, pzone=pzone)
    post_class, post_plays = _plays_for(post_location, pct, purge, pzone=pzone)
    plays = sorted(set(pre_plays) | set(post_plays))
    unswept = [
        row["kind"]
        for row in context.get("levels") or []
        if row["kind"] in {"asia_high", "asia_low", "london_high", "london_low", "onh", "onl"}
    ]
    if post_class == "single_break" and "single_break" in post_plays:
        primary = "single_break"
    elif "double_break" in post_plays:
        primary = "double_break"
    elif "big_range_eq" in post_plays:
        primary = "big_range_eq"
    else:
        primary = "london"
    return {
        "classification": post_class,
        "classification_pre_open": pre_class,
        "plays": plays,
        "plays_pre_open": sorted(set(pre_plays)),
        "plays_post_open": sorted(set(post_plays)),
        "primary_play": primary,
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
        },
        "unavailable_inputs": ["sister_index_relative_strength", "news_calendar"],
        "rule": "single break when the open is outside prior value on the side the overnight already purged, or the range exceeds 1.2% of price; otherwise the double-break / Judas play; the EQ play in addition on a big 6-9 range or an open inside value; London runs on its own clock; the 09:00 read governs entries before 09:30, the RTH open read the rest",
    }


def _purge_state(market, prior_day: Mapping[str, Any] | None) -> dict[str, Any]:
    """Which overnight liquidity was already taken before 09:00."""
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
    if not getattr(market, "jj_sessionstat", False):
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
        "minimum_average": min(_mean(highs), _mean(lows)),
        "expansion_0_5_high": _mean(highs) * Decimal("1.5"),
        "expansion_0_5_low": _mean(lows) * Decimal("1.5"),
    }
    setattr(market, cache_key, result)
    return result


# ---------------------------------------------------------------------------
# confirmation signatures (audit 1.2: faithful, kept unchanged)


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
        if side == "long":
            swept, closed, stop = s_l < f_l, t_c > s_h, s_l - TICK
        else:
            swept, closed, stop = s_h > f_h, t_c < s_l, s_h + TICK
        if swept and closed:
            return {
                "ok": True,
                "kind": "orderblock",
                "at": int(third["known_at"]),
                "entry": t_c,
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
            wick, closed, band, stop = body_lo - s_l, c_c > s_h, [s_l, body_lo], s_l - TICK
        else:
            wick, closed, band, stop = s_h - body_hi, c_c < s_l, [body_hi, s_h], s_h + TICK
        if wick > body and closed:
            return {
                "ok": True,
                "kind": "rejection_block",
                "at": int(close["known_at"]),
                "entry": c_c,
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
    vol_ok = True if avg_volume is None else _d(bar.get("V") or bar.get("volume") or 0) >= Decimal("1.5") * avg_volume
    return body <= Decimal("0.6") and vol_ok


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
    while index < len(rows) and len(cycles) < max_cycles:
        row = rows[index]
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None:
            index += 1
            continue
        if not (lo < level if side == "long" else hi > level):
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


MAX_CONTACTS_PER_LEVEL = 3


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
    max_contacts: int = MAX_CONTACTS_PER_LEVEL,
) -> list[dict[str, Any]]:
    """Each distinct test of a level, not only the first.

    The author trades a level whenever it is tested: 2025-10-07 buys the London
    quadrant at 04:30 after the session had already traded through it, and
    2026-06-05 buys R-Lo at 05:03 after two earlier round trips. A re-touch
    counts once price has left the level by ``departure``.
    """
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
        "session_date": str(market.day),
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
            "session_date": str(market.day),
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


FILL_MODES = ("at_level", "signature_close")


def _fill_modes(confirmed: Mapping[str, Any] | None, level: Decimal) -> list[tuple[str, Decimal | None, int | None]]:
    """The two fills of one signature: the limit at the level, and the market
    fill at the signature's own close.

    The author prints both: 2025-10-01 sells the +0.5 at 24,845 (the projection
    itself) and 2025-01-28 buys at 21,241.75, under the 21,258 low, on the
    reclaim candle. They are alternative fills of one opportunity, not two
    setups.
    """
    if confirmed is None:
        return [(mode, None, None) for mode in FILL_MODES]
    return [("at_level", level, confirmed["at"]), ("signature_close", confirmed["entry"], confirmed["at"])]


def _judas_episode(
    market,
    context: Mapping[str, Any],
    box: Mapping[str, Any],
    *,
    side: str,
    level: Decimal,
    kind: str,
    location_kind: str,
    contact,
    pack: Mapping[str, Any],
    begin: int,
    extra_values: Mapping[str, Any] | None = None,
    extra_location: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    modal_lo, modal_hi = _at(market, MODAL_WINDOW[0]), _at(market, MODAL_WINDOW[1])
    confirmed = pack.get("confirmed")
    ladder = objective_ladder(box, side)
    in_modal = contact is not None and modal_lo <= int(contact["start"]) < modal_hi
    out: list[dict[str, Any]] = []
    for mode, entry, at_ns in _fill_modes(confirmed, level):
        stop = None if confirmed is None else confirmed["stop"]
        anchor = entry if entry is not None else level
        forward = [row for row in ladder if sign(side) * (row["price"] - anchor) > 0]
        target = forward[0]["price"] if forward else None
        stages = [
            _context_stage(context, begin, branch="judas_reversal", location_kind=location_kind),
            _stage("reference", "pass", int((extra_location or {}).get("known_at") or box["known_at"]), id=box["id"], level=level, kind=kind, box_low=box["low"], box_high=box["high"], width=box["width"]),
            _stage(
                "location",
                "pass" if contact is not None and (extra_location or {}).get("verdict", "pass") == "pass" else "fail",
                None if contact is None else int(contact["start"]),
                level=level,
                kind=kind,
                location_kind=location_kind,
                **{
                    "reason": None if contact is not None else "level_not_contacted_in_the_window",
                    **{k: v for k, v in (extra_location or {}).items() if k not in {"verdict", "known_at"}},
                },
            ),
            _stage("trigger", "pass" if contact is not None else "fail", None if contact is None else int(contact["end"]), in_modal_window=in_modal, modal_window=list(MODAL_WINDOW)),
            _stage(
                "confirmation",
                pack.get("verdict", "fail"),
                at_ns,
                mode=mode,
                ob_2m=pack.get("ob_2m"),
                ob_3m=pack.get("ob_3m"),
                ob_5m=pack.get("ob_5m"),
                rejection_block=pack.get("rejection_block"),
                absorption=pack.get("absorption"),
                kind=None if confirmed is None else confirmed["kind"],
                timeframe_seconds=None if confirmed is None else confirmed.get("timeframe_seconds"),
            ),
            _stage("risk", "pass" if entry is not None and stop is not None and sign(side) * (entry - stop) > 0 else "fail", at_ns, entry=entry, stop=stop, stop_source="confirmation band"),
            _stage("objective", "pass" if entry is not None and target is not None and sign(side) * (target - entry) > 0 else "fail", at_ns, ladder=[{"name": row["name"], "price": row["price"]} for row in ladder], first_objective=target),
            _stage("management", "pass", at_ns, scale_out="along the ladder"),
        ]
        values = {
            "reference_px": level,
            "reference_kind": kind,
            "location_kind": location_kind,
            "cycle": (extra_values or {}).get("cycle", 0),
            "in_modal_window": in_modal,
            "confirmation_mode": mode,
            "signature": None if confirmed is None else confirmed["kind"],
            "confirmation_timeframe_seconds": None if confirmed is None else confirmed.get("timeframe_seconds"),
        }
        if extra_values:
            values.update({k: v for k, v in extra_values.items() if k != "cycle"})
        out.append(
            _episode(
                market,
                branch="judas_reversal",
                side=side,
                stages=stages,
                decision_at=at_ns,
                entry=entry,
                stop=stop,
                target=target,
                reference=box,
                trigger=contact,
                values=values,
                geometry={"ladder": [{"name": row["name"], "price": row["price"]} for row in ladder], "first_objective": target},
            )
        )
    return out


def _empty_pack() -> dict[str, Any]:
    return {"verdict": "fail", "confirmed": None, "ob_2m": None, "ob_3m": None, "ob_5m": None, "rejection_block": None, "absorption": None}


def _scan_judas_reversal(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The double-break / Judas day.

    Three location kinds, all traded on the rejection signature printed AT the
    level (coordinator guidance J-A and J-D, 2026-09-17):

    * the exhaustion projections +/-0.33, +/-0.5 and +/-0.66, which is where the
      author actually sells and buys on these days;
    * a drawn liquidity level that has been swept into the exhaustion area;
    * the box edge itself on the first rejection printed there, without waiting
      for a sweep and reclaim (2025-10-13 sells the HIGH at 09:03-09:05 and
      then buys the LOW reclaim at 09:40).
    """
    context = session_context(market)
    box = context.get("box")
    if box is None:
        return [], [{"reason": "ny_range_unavailable", "branch": "judas_reversal"}]
    begin, end = _at(market, NY_ACTION[0]), _at(market, NY_ACTION[1])
    episodes: list[dict[str, Any]] = []

    def confirm_at(contact, side, level):
        if contact is None:
            return _empty_pack()
        return confirm_pack(market, int(contact["end"]), side, level, min(end, int(contact["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))

    # 1. the exhaustion projections
    for name, side in (
        ("plus_0.33", "short"),
        ("plus_0.5", "short"),
        ("plus_0.66", "short"),
        ("minus_0.33", "long"),
        ("minus_0.5", "long"),
        ("minus_0.66", "long"),
    ):
        price = box["ladder"][name]
        touches = level_contacts(market, level=price, begin=begin, end=end, departure=box["width"] / 20)
        for index, touch in enumerate(touches or [None]):
            episodes.extend(
                _judas_episode(
                    market, context, box,
                    side=side, level=price, kind=name, location_kind="exhaustion_projection",
                    contact=touch, pack=confirm_at(touch, side, price), begin=begin,
                    extra_values={"cycle": index},
                    extra_location={"reason": None if touch is not None else "projection_not_reached"},
                )
            )

    # 2. the box edge on the first rejection printed there
    for name, side, price in (("box_high", "short", box["high"]), ("box_low", "long", box["low"])):
        touches = level_contacts(market, level=price, begin=begin, end=end, departure=box["width"] / 20)
        for index, touch in enumerate(touches or [None]):
            episodes.extend(
                _judas_episode(
                    market, context, box,
                    side=side, level=price, kind=name, location_kind="edge_rejection",
                    contact=touch, pack=confirm_at(touch, side, price), begin=begin,
                    extra_values={"cycle": index},
                )
            )

    # 3. a drawn liquidity level swept into the exhaustion area
    for level_row in context["levels"]:
        side = level_row["side"]
        level = level_row["price"]
        if int(level_row["known_at"]) > begin:
            continue
        for cycle in sweep_cycles(market, level=level, side=side, begin=begin, end=end):
            extreme = cycle["extreme"]
            edge = box["low"] if side == "long" else box["high"]
            depth = (edge - extreme) if side == "long" else (extreme - edge)
            reach = exhaustion_hit(context, extreme, side, exclude_kind=level_row["kind"])
            pack = confirm_pack(
                market,
                max(int(cycle["sweep"]["end"]), begin),
                side,
                level,
                min(end, int(cycle["sweep"]["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE),
            )
            episodes.extend(
                _judas_episode(
                    market, context, box,
                    side=side, level=level, kind=level_row["kind"], location_kind="swept_liquidity",
                    contact=cycle["sweep"], pack=pack, begin=begin,
                    extra_values={"cycle": cycle["cycle"], "sweep_extreme": extreme, "depth_class": depth_class(depth, box["width"])},
                    extra_location={
                        "verdict": "pass" if reach["reached"] else "fail",
                        "sweep_extreme": extreme,
                        "depth_points": depth,
                        "depth_class": depth_class(depth, box["width"]),
                        "in_mean_reversal_band": reach["in_band"],
                        "at_or_beyond_band": reach["at_or_beyond_band"],
                        "coincident_levels": reach["coincident"],
                        "reason": None if reach["reached"] else "sweep_short_of_exhaustion_area",
                    },
                )
            )
    return episodes, []


def _scan_judas_outbound(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Trade #1: at the open, take the break direction toward the projection.

    J-E (coordinator guidance 2026-09-17): 2026-07-16 breaks a drawn level at
    09:30-09:35 and the author sells 29,451.5 at 09:35 -- the first pullback to
    a box internal on the way down, not the opening minute's close. The trade is
    in the break direction, the objective is the opposite edge plus the half
    projection, and it is closed as the modal window arrives.
    """
    context = session_context(market)
    box = context.get("box")
    if box is None:
        return [], []
    open_ns = _at(market, "09:30")
    expiry = _at(market, MODAL_WINDOW[0])
    window_end = min(expiry, int(market.end))
    rows = _bars(market, open_ns, window_end, 60)
    if not rows:
        return [], []
    episodes: list[dict[str, Any]] = []
    # every level drawn before the open, plus the box edges, can be the level
    # the opening drive takes
    candidates = [{"kind": "box_high", "price": box["high"], "side": "short"}, {"kind": "box_low", "price": box["low"], "side": "long"}]
    for row in context.get("levels") or []:
        if int(row["known_at"]) <= open_ns:
            candidates.append({"kind": row["kind"], "price": row["price"], "side": row["side"]})
    internals = [
        {"kind": "eq", "price": box["eq"]},
        {"kind": "q25", "price": box["q25"]},
        {"kind": "q75", "price": box["q75"]},
        {"kind": "range_open", "price": box["range_open"]},
    ]
    seen: set[tuple] = set()
    for item in candidates:
        level = item["price"]
        # the opening drive takes the level: a break downward is a short, a
        # break upward is a long
        for direction, broke in (("short", any(_d(r["L"]) is not None and _d(r["L"]) < level for r in rows)),
                                 ("long", any(_d(r["H"]) is not None and _d(r["H"]) > level for r in rows))):
            if not broke:
                continue
            break_bar = next(
                r for r in rows
                if (direction == "short" and _d(r["L"]) is not None and _d(r["L"]) < level)
                or (direction == "long" and _d(r["H"]) is not None and _d(r["H"]) > level)
            )
            target = box["ladder"]["minus_0.5" if direction == "short" else "plus_0.5"]
            for internal in internals:
                price = internal["price"]
                if sign(direction) * (price - level) > 0:
                    continue  # the pullback is back toward the level, not beyond it
                fill = first_touch(market, level=price, begin=int(break_bar["end"]), end=window_end)
                key = (direction, internal["kind"], str(price))
                if key in seen:
                    continue
                seen.add(key)
                at_ns = None if fill is None else int(fill["known_at"])
                entry = None if fill is None else price
                stop = level
                stages = [
                    _context_stage(context, open_ns, branch="judas_outbound", broken_level=level, broken_kind=item["kind"]),
                    _stage("reference", "pass", box["known_at"], id=box["id"], level=level, kind=item["kind"], internal=internal["kind"]),
                    _stage("location", "pass", int(break_bar["start"]), level=level, broke=True, internal=internal["kind"], internal_price=price),
                    _stage("trigger", "pass", int(break_bar["end"]), expiry_ns=expiry, direction=direction),
                    _stage("confirmation", "pass" if fill is not None else "fail", at_ns, mode="pullback_to_internal", reason=None if fill is not None else "no_pullback_to_a_box_internal_before_the_modal_window"),
                    _stage("risk", "pass" if entry is not None and sign(direction) * (entry - stop) > 0 else "fail", at_ns, entry=entry, stop=stop),
                    _stage("objective", "pass" if entry is not None and sign(direction) * (target - entry) > 0 else "fail", at_ns, target=target, label="opposite edge + 0.5W projection"),
                    _stage("management", "pass", at_ns, exit_window=list(MODAL_WINDOW)),
                ]
                episodes.append(
                    _episode(
                        market,
                        branch="judas_outbound",
                        side=direction,
                        stages=stages,
                        decision_at=at_ns,
                        entry=entry,
                        stop=stop,
                        target=target,
                        reference=box,
                        trigger=break_bar,
                        values={"reference_px": price, "reference_kind": internal["kind"], "broken_level": level, "broken_kind": item["kind"], "cycle": 0, "confirmation_mode": "pullback_to_internal", "expiry_ns": expiry},
                        geometry={"first_objective": target},
                    )
                )
    return episodes, []


def _scan_extension_reaction(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """After 10:00, a touch of the 1.33-1.66 band beyond an edge with a
    rejection signature; reverse toward the range."""
    context = session_context(market)
    box = context.get("box")
    if box is None:
        return [], []
    bands = box["extension"]
    if not bands.get("available"):
        return [], [{"reason": "extension_band_unavailable", "branch": "extension_reaction"}]
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
    return episodes, []


def _scan_other_session(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """London: the 02:00-03:00 box traded 03:00-06:00 with the same internals.

    J8: the author's London entries on 2025-10-07 and 2025-10-08 came at the 25%
    line with no box-edge sweep; the edge raid is recorded as an operand, never
    required. J7: any of the 2/3/5-minute orderblock or the rejection block
    confirms, not the 3-minute one alone.
    """
    context = session_context(market)
    london = box_geometry(market, "london")
    begin, end = _at(market, "03:00"), _at(market, LONDON_ACTION[1])
    episodes: list[dict[str, Any]] = []
    locations: list[dict[str, Any]] = []
    if london is not None:
        for name, price, sides in (
            ("london_low", london["low"], ("long",)),
            ("q25", london["q25"], ("long", "short")),
            ("eq", london["eq"], ("long", "short")),
            ("q75", london["q75"], ("long", "short")),
            ("london_high", london["high"], ("short",)),
            ("minus_0.5", london["ladder"]["minus_0.5"], ("long",)),
            ("plus_0.5", london["ladder"]["plus_0.5"], ("short",)),
            ("minus_1.33", london["ladder"]["minus_1.33"], ("long",)),
            ("minus_1.66", london["ladder"]["minus_1.66"], ("long",)),
            ("plus_1.33", london["ladder"]["plus_1.33"], ("short",)),
            ("plus_1.66", london["ladder"]["plus_1.66"], ("short",)),
        ):
            for side in sides:
                locations.append({"kind": name, "price": price, "side": side, "known_at": london["known_at"], "from": begin})
    # Drawn levels are live through the whole London session, before the box closes
    # (2025-05-23: the prior RTH low is swept at 02:20, inside the box window).
    for row in context.get("levels") or []:
        if row["kind"] in {"box_low", "box_high"}:
            continue
        locations.append({**row, "from": max(_at(market, LONDON_ACTION[0]), int(row["known_at"]))})
    if london is None and not locations:
        return [], [{"reason": "london_range_unavailable", "branch": "other_session"}]
    edge_swept = None
    if london is not None:
        edge_swept = any(
            sweep_cycles(market, level=london[key], side=side, begin=begin, end=end, max_cycles=1)
            for key, side in (("low", "long"), ("high", "short"))
        )
    drawn = sorted(
        ({"price": row["price"], "kind": row["kind"], "known_at": int(row["known_at"])} for row in context.get("levels") or []),
        key=lambda row: row["price"],
    )
    for row in locations:
        side, level = row["side"], row["price"]
        start = max(int(row.get("from") or begin), int(row["known_at"]))
        box_frozen = london is not None and start >= int(london["known_at"])
        width = (london["width"] if london is not None else Decimal("40"))
        touches = level_contacts(market, level=level, begin=start, end=end, departure=width / 20)
        for contact_index, touch in enumerate(touches or [None]):
          pack = (
            confirm_pack(market, int(touch["end"]), side, level, min(end, int(touch["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))
            if touch is not None
            else {"verdict": "fail", "confirmed": None, "ob_2m": None, "ob_3m": None, "ob_5m": None, "rejection_block": None, "absorption": None}
          )
          confirmed = pack.get("confirmed")
          entry = None if confirmed is None else confirmed["entry"]
          at_ns = None if confirmed is None else confirmed["at"]
          stop = None if confirmed is None else confirmed["stop"]
          target = None
          if entry is not None:
            if box_frozen:
                ladder = objective_ladder(london, side)
                target = next((item["price"] for item in ladder if sign(side) * (item["price"] - entry) > 0), None)
            if target is None:
                # before the box freezes, the objective is the next drawn level
                forward = [
                    item["price"]
                    for item in drawn
                    if item["known_at"] <= at_ns and sign(side) * (item["price"] - entry) > 0
                ]
                target = (min(forward) if side == "long" else max(forward)) if forward else None
          stages = [
              _context_stage(context, start, branch="other_session", session="london", box_edge_swept=edge_swept, box_frozen=box_frozen),
              _stage(
                  "reference",
                  "pass",
                  int(row["known_at"]),
                  id=None if london is None else london["id"],
                  level=level,
                  kind=row["kind"],
                  box_low=None if not box_frozen else london["low"],
                  box_high=None if not box_frozen else london["high"],
                  box_frozen=box_frozen,
              ),
              _stage("location", "pass" if touch is not None else "fail", None if touch is None else int(touch["start"]), level=level, contact=None if touch is None else "touch", box_edge_swept=edge_swept, reason=None if touch is not None else "level_not_contacted_in_the_london_window"),
              _stage("trigger", "pass" if touch is not None else "fail", None if touch is None else int(touch["start"])),
              _stage("confirmation", pack["verdict"], at_ns, ob_2m=pack["ob_2m"], ob_3m=pack["ob_3m"], ob_5m=pack["ob_5m"], rejection_block=pack["rejection_block"], absorption=pack["absorption"], kind=None if confirmed is None else confirmed["kind"], any_of_2m_3m_5m=True),
              _stage("risk", "pass" if entry is not None and stop is not None and sign(side) * (entry - stop) > 0 else "fail", at_ns, entry=entry, stop=stop),
              _stage("objective", "pass" if entry is not None and target is not None and sign(side) * (target - entry) > 0 else "fail", at_ns, target=target, source="london ladder" if box_frozen else "next drawn level"),
              _stage("management", "pass", at_ns),
          ]
          episodes.append(
              _episode(
                  market,
                  branch="other_session",
                  side=side,
                  stages=stages,
                  decision_at=at_ns,
                  entry=entry,
                  stop=stop,
                  target=target,
                  reference=london or {"id": f"jj-london-levels:{market.instrument_id}:{market.day}"},
                  trigger=touch,
                  values={"reference_px": level, "reference_kind": row["kind"], "cycle": contact_index, "confirmation_mode": None if confirmed is None else confirmed["kind"], "box_edge_swept": edge_swept, "box_frozen": box_frozen},
                  geometry={"first_objective": target},
              )
          )
    return episodes, []


def _eq_locations(market, box: Mapping[str, Any], branch: str) -> list[dict[str, Any]]:
    """EQ, the quadrants, the range open and -- J3 -- the 15-minute opening range."""
    rows = [
        {"kind": "eq", "price": box["eq"], "known_at": box["known_at"]},
        {"kind": "q25", "price": box["q25"], "known_at": box["known_at"]},
        {"kind": "q75", "price": box["q75"], "known_at": box["known_at"]},
        {"kind": "range_open", "price": box["range_open"], "known_at": box["known_at"]},
    ]
    if branch == "internal_rotation":
        rows.append({"kind": "box_low", "price": box["low"], "known_at": box["known_at"]})
        rows.append({"kind": "box_high", "price": box["high"], "known_at": box["known_at"]})
    if branch in {"single_extended", "single_purged"}:
        span = _span(_bars(market, _at(market, "09:30"), _at(market, "09:45"), 60), known_at=_at(market, "09:45"))
        if span is not None:
            mid = (span["low"] + span["high"]) / 2
            rows.append({"kind": "or15_mid", "price": mid, "known_at": _at(market, "09:45")})
            rows.append({"kind": "or15_q25", "price": span["low"] + (span["high"] - span["low"]) / 4, "known_at": _at(market, "09:45")})
            rows.append({"kind": "or15_q75", "price": span["low"] + (span["high"] - span["low"]) * 3 / 4, "known_at": _at(market, "09:45")})
    return rows


def _context_sides(branch: str, context: Mapping[str, Any]) -> tuple[str, ...]:
    """Which way the day's read points. J10: the purge admits both directions.

    The single-break branches read the location of the RTH open, which is what
    the author quotes ("RTH open below the prior RTH value low", 2026-07-28);
    the rotation branch reads the same location.
    """
    label = context.get("rth_open_location") or context.get("open_location")
    purge = context.get("purge") or {}
    if branch == "internal_rotation":
        # "same framework when having a big 6-9 range > long/short the EQ": the
        # EQ play runs both ways on every day (J-C).
        return ("long", "short")
    if branch == "single_purged":
        if not purge.get("available"):
            return ()
        sides: list[str] = []
        if purge.get("purged_high") is True:
            sides.append("long")
        if purge.get("purged_low") is True:
            sides.append("short")
        return tuple(sides)
    if branch == "single_extended":
        # the side is the break the session shows, read at the entry time by
        # ``break_state``; both are enumerated and the operand records which
        return ("long", "short")
    return ("long", "short")


def break_state(market, box: Mapping[str, Any], at_ns: int) -> dict[str, Any]:
    """Which box edge has been broken by ``at_ns``, and which is untouched.

    J-C: "single break behaviour through A period, range mid provided the entry
    area" (2026-07-27) -- the play is admissible when one edge has gone and the
    other has not, and the side is the break's own direction.
    """
    rows = _bars(market, _at(market, "09:00"), int(at_ns), 60)
    high = max((_d(row["H"]) for row in rows if row.get("H") is not None), default=None)
    low = min((_d(row["L"]) for row in rows if row.get("L") is not None), default=None)
    broke_high = high is not None and high > box["high"]
    broke_low = low is not None and low < box["low"]
    side = None
    if broke_high and not broke_low:
        side = "long"
    elif broke_low and not broke_high:
        side = "short"
    return {"broke_high": broke_high, "broke_low": broke_low, "single_break": side is not None, "side": side}


def _scan_eq_branch(market, branch: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    context = session_context(market)
    box = context.get("box")
    if box is None:
        return [], []
    size = context["range_class"]
    sides = _context_sides(branch, context)
    if branch == "single_extended":
        # the open location is the branch's own input, so the window starts at
        # the open; "out by 10:00" is carried on the management stage
        begin, end = _at(market, "09:30"), _at(market, "10:30")
    elif branch == "single_purged":
        begin, end = _at(market, "09:30"), _at(market, "12:00")
    else:
        begin, end = _at(market, "09:00"), _at(market, "16:00")
    episodes: list[dict[str, Any]] = []
    modal_lo, modal_hi = _at(market, MODAL_WINDOW[0]), _at(market, MODAL_WINDOW[1])
    for row in _eq_locations(market, box, branch):
        for side in sides:
            start = max(begin, int(row["known_at"]))
            touches = level_contacts(market, level=row["price"], begin=start, end=end, departure=box["width"] / 20)
            for contact_index, touch in enumerate(touches or [None]):
             state = break_state(market, box, int(touch["start"])) if touch is not None else {"single_break": None, "side": None, "broke_high": None, "broke_low": None}
             if branch == "single_extended" and touch is not None and state["side"] != side:
                continue
             pack = (
                 confirm_pack(market, int(touch["end"]), side, row["price"], min(end, int(touch["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))
                 if touch is not None
                 else {"verdict": "fail", "confirmed": None, "ob_2m": None, "ob_3m": None, "ob_5m": None, "rejection_block": None, "absorption": None}
             )
             confirmed = pack.get("confirmed")
             entry = None if confirmed is None else confirmed["entry"]
             at_ns = None if confirmed is None else confirmed["at"]
             stop = None if confirmed is None else confirmed["stop"]
             if branch == "single_purged":
                 # J12: the objective is the projection, not the range edge.
                 target = box["ladder"]["plus_1.33" if side == "long" else "minus_1.33"]
             else:
                 target = box["high"] if side == "long" else box["low"]
             in_add_window = touch is not None and modal_lo <= int(touch["start"]) < modal_hi
             reduced = at_ns is not None and at_ns >= _at(market, "10:00")
             stages = [
                 _context_stage(
                     context,
                     begin,
                     branch=branch,
                     range_gate=">=0.3% for the single-break cases" if branch.startswith("single") else "inside prior value",
                     evrange=context.get("evrange"),
                 ),
                 _stage("reference", "pass", max(int(box["known_at"]), int(row["known_at"])), id=box["id"], level=row["price"], kind=row["kind"], box_low=box["low"], box_high=box["high"], width=box["width"]),
                 _stage(
                     "location",
                     "pass" if touch is not None else "fail",
                     None if touch is None else int(touch["start"]),
                     level=row["price"],
                     single_break=state["single_break"],
                     broke_high=state["broke_high"],
                     broke_low=state["broke_low"],
                     reason=None if touch is not None else "level_not_contacted_in_window",
                 ),
                 _stage("trigger", "pass" if touch is not None else "fail", None if touch is None else int(touch["start"]), add_window=list(MODAL_WINDOW), in_add_window=in_add_window),
                 _stage("confirmation", pack["verdict"], at_ns, ob_2m=pack["ob_2m"], ob_3m=pack["ob_3m"], ob_5m=pack["ob_5m"], rejection_block=pack["rejection_block"], absorption=pack["absorption"], kind=None if confirmed is None else confirmed["kind"]),
                 _stage("risk", "pass" if entry is not None and stop is not None and sign(side) * (entry - stop) > 0 else "fail", at_ns, entry=entry, stop=stop),
                 _stage("objective", "pass" if entry is not None and sign(side) * (target - entry) > 0 else "fail", at_ns, target=target, label="projection" if branch == "single_purged" else "range edge"),
                 _stage("management", "pass", at_ns, reduced_expectations=reduced, out_by_1000=branch == "single_extended"),
             ]
             episodes.append(
                 _episode(
                     market,
                     branch=branch,
                     side=side,
                     stages=stages,
                     decision_at=at_ns,
                     entry=entry,
                     stop=stop,
                     target=target,
                     reference=box,
                     trigger=touch,
                     values={"reference_px": row["price"], "reference_kind": row["kind"], "cycle": contact_index, "confirmation_mode": None if confirmed is None else confirmed["kind"], "range_bin": size.get("bin"), "in_add_window": in_add_window},
                     geometry={"first_objective": target},
                 )
             )
    return episodes, []


def _scan_pzone(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """P-zones are proprietary: only the author's printed boxes are available.

    J-G: the fill is the limit inside the printed zone (2026-01-09 buys
    25,664.25 inside the 25,655-25,665 box), with the signature close as the
    alternative fill of the same opportunity.
    """
    context = session_context(market)
    box = context.get("box")
    zones = PZONE_FIXTURES.get(str(market.day))
    if not zones:
        return [], [{"reason": "pzone_generator_unknown", "branch": "timed_pzone_reversal", "operand": "pzone_generator"}]
    episodes: list[dict[str, Any]] = []
    for zone in zones:
        anchor = zone.get("anchor", "09:00")
        begin = _at(market, anchor)
        end = min(_at(market, "12:00"), int(market.end))
        side = zone.get("side") or ("long" if box is None or zone["high"] < box["eq"] else "short")
        level = (zone["low"] + zone["high"]) / 2
        touch = first_touch(market, level=level, begin=begin, end=end)
        pack = (
            confirm_pack(market, int(touch["end"]), side, level, min(end, int(touch["end"]) + CONFIRM_HORIZON_MIN * NS_MINUTE))
            if touch is not None
            else {"verdict": "unknown", "confirmed": None, "ob_2m": None, "ob_3m": None, "ob_5m": None, "rejection_block": None, "absorption": None}
        )
        confirmed = pack.get("confirmed")
        target = zone.get("target") or (None if box is None else (box["high"] if side == "long" else box["low"]))
        for mode, entry, at_ns in _fill_modes(confirmed, level):
            stop = None if confirmed is None else confirmed["stop"]
            stages = [
                _context_stage(context, begin, branch="timed_pzone_reversal", anchor=anchor, pzone_source="author_printed_fixture"),
                _stage("reference", "pass", begin, zone=[zone["low"], zone["high"]], anchor=anchor),
                _stage("location", "pass" if touch is not None else "fail", None if touch is None else int(touch["start"]), zone=[zone["low"], zone["high"]]),
                _stage("trigger", "pass" if touch is not None else "fail", None if touch is None else int(touch["end"])),
                _stage("confirmation", pack["verdict"], at_ns, mode=mode, kind=None if confirmed is None else confirmed["kind"], absorption=pack["absorption"], timeframe_seconds=None if confirmed is None else confirmed.get("timeframe_seconds")),
                _stage("risk", "pass" if entry is not None and stop is not None and sign(side) * (entry - stop) > 0 else "fail", at_ns, entry=entry, stop=stop),
                _stage("objective", "pass" if entry is not None and target is not None and sign(side) * (target - entry) > 0 else "fail", at_ns, target=target),
                _stage("management", "pass", at_ns),
            ]
            episodes.append(
                _episode(
                    market,
                    branch="timed_pzone_reversal",
                    side=side,
                    stages=stages,
                    decision_at=at_ns,
                    entry=entry,
                    stop=stop,
                    target=target,
                    reference={"id": f"pzone:{market.day}:{zone['low']}-{zone['high']}", "low": zone["low"], "high": zone["high"]},
                    trigger=touch,
                    values={"reference_px": level, "reference_kind": "pzone", "cycle": 0, "confirmation_mode": mode, "pzone_anchor": anchor, "pzone": [zone["low"], zone["high"]]},
                    geometry={"first_objective": target},
                )
            )
    return episodes, [{"reason": "pzone_generator_unknown", "branch": "timed_pzone_reversal", "operand": "pzone_generator", "detail": "only the author's printed boxes are available"}]


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

# The author's clock: the 09:00-12:00 "three-hour candle" plus the London
# 03:00-06:00 action window; extension entries run to 16:00.
SELECTION_CLOCK = ("02:00", "16:00")


def _rec_branch(rec: Any) -> str | None:
    if rec is None:
        return None
    if isinstance(rec, str):
        return rec
    if isinstance(rec, Mapping):
        value = rec.get("branch") or rec.get("source_branch")
        return None if value is None else str(value)
    return None


def selection_for(market, episodes, *, primary_play: str | None = None) -> dict[str, Any]:
    """The author's trade list: the chosen play first, at most three entries."""
    bars = _bars(market, int(market.start), int(market.end), 60)
    clock_window = (_at(market, SELECTION_CLOCK[0]), _at(market, SELECTION_CLOCK[1]))
    chosen = [ep for ep in episodes if (ep.get("values") or {}).get("play") == primary_play] if primary_play else list(episodes)
    result = select_session_trades(chosen, bars=bars, clock=clock_window, max_entries=MAX_ENTRIES_PER_SESSION)
    fallback = False
    if not result["n_entries"] and primary_play:
        rest = [ep for ep in episodes if (ep.get("values") or {}).get("play") != primary_play]
        if rest:
            result = select_session_trades(rest, bars=bars, clock=clock_window, max_entries=MAX_ENTRIES_PER_SESSION)
            fallback = bool(result["n_entries"])
    result["primary_play"] = primary_play
    result["fallback_play_used"] = fallback
    return result


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
    allowed = set(read.get("plays") or ())
    episodes: list[dict[str, Any]] = []
    omissions: list[dict[str, Any]] = []
    for item in branches:
        scanner = _SCANNERS.get(item)
        if scanner is None:
            omissions.append({"reason": "unknown_branch", "branch": item})
            continue
        play = PLAY_OF_BRANCH.get(item)
        if play not in allowed:
            omissions.append({"reason": "play_not_in_the_day_read", "branch": item, "play": play, "classification": read.get("classification")})
            continue
        try:
            part, omit = scanner(market)
        except Exception as exc:
            omissions.append({"reason": "scan_error", "branch": item, "error": f"{type(exc).__name__}: {exc}"})
            continue
        episodes.extend(part)
        omissions.extend(omit)
    episodes = list(enumeration_point("contacts", episodes, market=market, family=FAMILY) or episodes)
    open_ns = _at(market, "09:30")
    pre_open_plays = set(read.get("plays_pre_open") or ())
    for episode in episodes:
        play = PLAY_OF_BRANCH.get(episode.get("branch"))
        episode["values"]["play"] = play
        episode["values"]["is_primary_play"] = play == read.get("primary_play")
        decided = episode.get("decision_at")
        readable = play in pre_open_plays if (decided is not None and int(decided) < open_ns) else True
        episode["values"]["read_used"] = "09:00" if (decided is not None and int(decided) < open_ns) else "09:30"
        if not readable and episode.get("research_verdict") == "pass":
            episode["research_verdict"] = "fail"
            episode["failed"] = list(episode.get("failed") or []) + ["context"]
            episode["strategy_assessment"]["status"] = "no_setup"
            for stage in episode["stages"]:
                if stage["stage"] == "context":
                    stage["verdict"] = "fail"
                    stage["operands"]["reason"] = "play_not_readable_before_the_open"
    selection = selection_for(market, episodes, primary_play=read.get("primary_play"))
    label = branch if branch and branch in _SCANNERS else "B0.3"
    return finish(_document(market, label, episodes, omissions, selection=selection, day_read=read))


# ---------------------------------------------------------------------------
# rules


RULES = {
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
        "JJ-OR15-retracement": _eq_locations,
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
    day = market.day
    if date_text:
        try:
            day = date.fromisoformat(str(date_text)[:10])
        except ValueError:
            day = market.day
    offset = (day - market.day).days
    if hour >= 18:
        offset -= 1
    try:
        return int(market.at(f"{hour:02d}:{minute:02d}", offset))
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


def match_entry(market, episodes, entry, *, strict_points: Decimal = REPLAY_LEVEL_TOLERANCE) -> dict[str, Any]:
    """Does any episode produce this narrated entry, on this side, at this time?

    Where the post prints a fill the comparison is entry price to fill price.
    Where the post narrates the trade without printing a fill, the comparison is
    our reference level to the level the post names.
    """
    window = _printed_window_ns(market, entry.get("date"), entry.get("time_et"))
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
    want_play = PLAY_OF_BRANCH.get(entry.get("branch"))
    for ep in episodes:
        if ep.get("research_verdict") != "pass" or ep.get("side") != side:
            continue
        if want_play is not None and PLAY_OF_BRANCH.get(ep.get("branch")) != want_play:
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
    in_time = [row for row in rows if row["bars_from_printed"] is not None and row["bars_from_printed"] <= 1.0]
    want_branch = entry.get("branch")
    if in_time:
        scored = sorted(
            in_time,
            key=lambda row: (
                0 if want_branch and row["branch"] == want_branch else 1,
                Decimal("1e9") if row["delta_points"] is None else row["delta_points"],
            ),
        )
    else:
        scored = sorted(
            rows,
            key=lambda row: (
                9e9 if row["bars_from_printed"] is None else row["bars_from_printed"],
                0 if want_branch and row["branch"] == want_branch else 1,
            ),
        )
    best = scored[0] if scored else None
    ok_time = best is not None and best["bars_from_printed"] is not None and best["bars_from_printed"] <= 1.0
    no_price = compare_to is None
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
            and PLAY_OF_BRANCH.get(best["branch"]) == PLAY_OF_BRANCH.get(entry.get("branch"))
        ),
        "detected_strict": bool(
            best
            and ok_time
            and best["delta_points"] is not None
            and best["delta_points"] <= strict_points
            and PLAY_OF_BRANCH.get(best["branch"]) == PLAY_OF_BRANCH.get(entry.get("branch"))
        ),
        "detected_within_3_bars": bool(
            best
            and best["bars_from_printed"] is not None
            and best["bars_from_printed"] <= 3.0
            and (no_price or (best["delta_points"] is not None and best["delta_points"] <= tolerance))
            and PLAY_OF_BRANCH.get(best["branch"]) == PLAY_OF_BRANCH.get(entry.get("branch"))
        ),
        "our_entry": None if best is None else float(best["value"]),
        "our_entry_ns": None if best is None else best["at_ns"],
        "our_branch": None if best is None else best["branch"],
        "our_mode": None if best is None else best["mode"],
        "our_reference": None if best is None else best["reference_kind"],
        "our_play": None if best is None else PLAY_OF_BRANCH.get(best["branch"]),
        "expected_play": PLAY_OF_BRANCH.get(entry.get("branch")),
        "play_matches": None if best is None else PLAY_OF_BRANCH.get(best["branch"]) == PLAY_OF_BRANCH.get(entry.get("branch")),
        "delta_points": None if best is None or best["delta_points"] is None else float(best["delta_points"]),
        "bars_from_printed": None if best is None or best["bars_from_printed"] is None else float(best["bars_from_printed"]),
        "n_pass_episodes": len(rows),
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
