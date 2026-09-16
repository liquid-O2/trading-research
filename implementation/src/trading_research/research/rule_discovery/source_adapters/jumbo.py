"""P15-09 Jumbo range branches."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping
import inspect
import json

from trading_research.research.contracts.types import RuleSpec
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

NS_MINUTE = 60_000_000_000
TICK = Decimal("0.25")
REPLAY_LEVEL_TOLERANCE = Decimal("2")
TAPE_FIRST = date(2020, 1, 2)
TAPE_LAST = date(2026, 8, 19)
OUTSIDE_TAPE = "date outside the tape"
STAGE_ORDER = ("context", "reference", "location", "trigger", "confirmation", "risk", "objective", "management")
LADDER_MULT = (Decimal("0.5"), Decimal("1"), Decimal("1.33"), Decimal("1.66"), Decimal("2"), Decimal("2.5"), Decimal("3"))
TRACK_DIR = Path("/workspace/.worktrees/b02-jumbo/implementation/reports/research-work/P15-16A/_track_jumbo")

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
        {"low": Decimal("25785"), "high": Decimal("25795"), "anchor": "09:00", "session": 1, "width_od": True},
        {"low": Decimal("25740"), "high": Decimal("25750"), "anchor": "09:00", "session": 1, "width_od": True},
        {"low": Decimal("25677"), "high": Decimal("25687"), "anchor": "09:00", "session": 1, "width_od": True},
        {"low": Decimal("25630"), "high": Decimal("25640"), "anchor": "09:00", "session": 1, "width_od": True},
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

RULES = {
    "RR-01-extension-band-1.33-1.66": {"kind": "literal", "source": "JR p.23; o015", "finding": "RR-01"},
    "RR-01-OD-near-band-0.33-0.66": {"kind": "OD", "source": "OD:historical scanner band, not source", "finding": "RR-01"},
    "RR-03-sweep-from-09:00": {"kind": "literal", "source": "JR p.20", "finding": "RR-03"},
    "RR-03-modal-reversal-09:40-09:50": {"kind": "literal", "source": "JR p.70", "finding": "RR-03"},
    "RR-03-extension-after-10:00": {"kind": "literal", "source": "JR pp.25-26", "finding": "RR-03"},
    "RR-04-london-02:00-03:00": {"kind": "literal", "source": "JR pp.50, 63-64", "finding": "RR-04"},
    "RR-05-pzone-anchors": {"kind": "literal", "source": "JR pp.16-18", "finding": "RR-05"},
    "RR-05-OD-absorption-proxy": {
        "kind": "OD",
        "source": "OD:TBR p.35 body<=0.6 vol>=1.5x14-period average",
        "finding": "RR-05",
        "parameters": {"body_ratio_max": "0.6", "volume_mult": "1.5", "volume_lookback": 14},
    },
    "RR-06-reclaim-entry": {"kind": "literal", "source": "JR p.71", "finding": "RR-06"},
    "RR-06-objective-plus-0.5": {"kind": "literal", "source": "JR p.71", "finding": "RR-06"},
    "RR-06-projection-ladder": {"kind": "literal", "source": "JR pp.16-18", "finding": "RR-06"},
    "RR-06-sweep-depth-recorded": {"kind": "literal", "source": "F11; RR-06", "finding": "F11"},
    "RR-07-OD-sessionstat-60": {"kind": "OD", "source": "OD:60-session mean/median of selected clock from native tape", "finding": "RR-07"},
    "RR-07-evrange-fixture": {"kind": "literal", "source": "F17; JR pp.30-33", "finding": "RR-07"},
    "RR-08-open-location-at-09:30": {"kind": "literal", "source": "JR pp.36, 38, 42", "finding": "RR-08"},
    "RR-08-OD-branch-selector": {"kind": "OD", "source": "OD:TBR pp.12-24 no numeric threshold", "finding": "RR-08"},
    "RR-09-published-statistics": {"kind": "literal", "source": "JR pp.23, 37, 70", "finding": "RR-09"},
    "RR-09-bigtrades-deferred": {
        "kind": "OD",
        "source": "deferred: JR p.50 BigTrades NQ >=100 NY / >=75 London; JR pp.49-50 35% footprint filter is a different flow view; neither series is on the native tape",
        "finding": "RR-09",
        "status": "deferred",
    },
    "F08-single-extended-reduced-after-10:00": {"kind": "literal", "source": "TBR p.12", "finding": "F08"},
    "RR-02-eq-both-sides-context-bound": {
        "kind": "literal",
        "source": "TBR pp.12-15; JR 2026-09-01/02 EQ both ways; RR-02",
        "finding": "RR-02",
    },
    "F11-confirm-3m-ob-baseline": {"kind": "literal", "source": "TBR p.27 C2 sweeps C1, C3 closes beyond C2 opposite extreme (O056)", "finding": "F11"},
    "F11-OD-confirm-2m-5m-rejection": {"kind": "OD", "source": "OD:2m/5m OB and rejection-block TBR p.29 close above sweep candle", "finding": "F11"},
    "F11-confirm-any-2-3-5-or-rejection": {
        "kind": "literal",
        "source": "TBR pp.27-29; F11 any of 2m/3m/5m full-C2 OB or rejection block",
        "finding": "F11",
    },
    "F12-candidate-references-unchanged": {"kind": "literal", "source": "F12 note only", "finding": "F12"},
    "F17-pzone-generator-unknown": {"kind": "OD", "source": "OD:proprietary P-zone generator unknown", "finding": "F17"},
    "F18-ny-clock-ET": {"kind": "literal", "source": "TBR p.6", "finding": "F18"},
    "F19-chart-clocks-UK-UTC": {"kind": "literal", "source": "JR p.71 ticket UTC; 2026 NT charts UK", "finding": "F19"},
}


def _d(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def extension_reaction_bands(high, low, width=None) -> dict[str, Any]:
    """RR-01: o015 edge ± [1.33, 1.66]·W."""
    from trading_research.research.method_pack.objects.range_geometry import o015

    high_d, low_d = _d(high), _d(low)
    assert high_d is not None and low_d is not None
    width_d = _d(width) if width is not None else (high_d - low_d)
    result = o015(
        {
            "H": high_d,
            "L": low_d,
            "W": width_d,
            "coordinate_convention_verified": True,
            "parent_id": "jj-tbr-b02",
        }
    )
    value = result.value or {}
    upper = value.get("upper_band")
    lower = value.get("lower_band")
    if not upper or not lower or len(upper) < 2 or len(lower) < 2:
        return {"upper": None, "lower": None, "width": width_d, "available": False, "reason": result.reason}
    return {
        "upper": [Decimal(str(upper[0])), Decimal(str(upper[1]))],
        "lower": [Decimal(str(lower[0])), Decimal(str(lower[1]))],
        "width": width_d,
        "available": True,
    }


def mean_reversal_bands(high, low) -> dict[str, Any]:
    """RR-01 OD / RR-06: edge ± [0.33, 0.66]·W. Not the extension_reaction location."""
    high_d, low_d = _d(high), _d(low)
    assert high_d is not None and low_d is not None
    width_d = high_d - low_d
    return {
        "upper": [high_d + Decimal("0.33") * width_d, high_d + Decimal("0.66") * width_d],
        "lower": [low_d - Decimal("0.66") * width_d, low_d - Decimal("0.33") * width_d],
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
    if hasattr(market, "at") and callable(getattr(market, "at")):
        try:
            return int(market.at(hhmm, offset))
        except TypeError:
            if offset == 0:
                return int(market.at(hhmm))
    day = _as_day(market)
    if day is None:
        raise ValueError("market has no day for clock conversion")
    day = day + timedelta(days=offset)
    hour_s, minute_s = hhmm.split(":")
    from trading_research.research.method_pack.clocks import et_ns

    return et_ns(day, int(hour_s), int(minute_s))


def _bar_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        start = int(row.get("start") or row.get("start_ns") or 0)
        end = int(row.get("end") or row.get("end_ns") or start + NS_MINUTE)
        known = row.get("known_at") or row.get("available_at_ns") or end
        return {
            "start": start,
            "end": end,
            "O": _d(row.get("O") or row.get("open")),
            "H": _d(row.get("H") or row.get("high")),
            "L": _d(row.get("L") or row.get("low")),
            "C": _d(row.get("C") or row.get("close")),
            "known_at": int(known),
            "volume": int(row.get("volume") or 0),
            "bar_id": str(row.get("bar_id") or start),
            "observed_complete": bool(row.get("observed_complete", True)),
        }
    start = int(row.start_ns)
    end = int(row.end_ns)
    known = int(getattr(row, "available_at_ns", end))
    return {
        "start": start,
        "end": end,
        "O": _d(getattr(row, "open", None)),
        "H": _d(getattr(row, "high", None)),
        "L": _d(getattr(row, "low", None)),
        "C": _d(getattr(row, "close", None)),
        "known_at": known,
        "volume": int(getattr(row, "volume", 0) or 0),
        "bar_id": str(getattr(row, "bar_id", start)),
        "observed_complete": True,
    }


def _bars(market, start: int, end: int, seconds: int = 60) -> list[dict[str, Any]]:
    if end <= start:
        return []
    rows: list[Any] = []
    if hasattr(market, "completed_bars"):
        try:
            rows = list(market.completed_bars(int(start), int(end), int(seconds)))
        except Exception:
            rows = []
    if not rows and hasattr(market, "bars"):
        try:
            rows = list(market.bars(start, end, seconds))
        except TypeError:
            rows = list(market.bars(start, end))
        except Exception:
            rows = []
    out = [_bar_dict(row) for row in rows]
    return [row for row in out if row["start"] < end and row["end"] > start]


def _span(bars: list[dict[str, Any]], known_at: int | None = None) -> dict[str, Any] | None:
    highs = [row["H"] for row in bars if row.get("H") is not None]
    lows = [row["L"] for row in bars if row.get("L") is not None]
    if not highs or not lows:
        return None
    last_known = bars[-1]["known_at"]
    return {
        "high": max(highs),
        "low": min(lows),
        "open": bars[0].get("O"),
        "close": bars[-1].get("C"),
        "known_at": known_at if known_at is not None else last_known,
        "start": bars[0]["start"],
        "end": bars[-1]["end"],
    }


def _cutoff(bars: list[dict[str, Any]], decision_at: int | None) -> list[dict[str, Any]]:
    if decision_at is None:
        return list(bars)
    return [row for row in bars if int(row["known_at"]) <= int(decision_at)]


def _first_sweep(bars: list[dict[str, Any]], side: str, edge: Decimal) -> dict[str, Any] | None:
    for row in bars:
        if side == "long" and row.get("L") is not None and row["L"] < edge:
            return row
        if side == "short" and row.get("H") is not None and row["H"] > edge:
            return row
    return None


def _sweep_cycles(
    bars: list[dict[str, Any]],
    side: str,
    edge: Decimal,
    modal_lo: int | None = None,
    modal_hi: int | None = None,
) -> list[tuple[dict[str, Any], dict[str, Any] | None]]:
    cycles: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    first = _first_sweep(bars, side, edge)
    seen: set[int] = set()
    if first is not None:
        cycles.append((first, _reclaim(bars, side, edge, first["end"])))
        seen.add(int(first["start"]))
    if modal_lo is not None and modal_hi is not None:
        modal = [row for row in bars if modal_lo <= row["start"] < modal_hi]
        later = _first_sweep(modal, side, edge)
        if later is not None and int(later["start"]) not in seen:
            cycles.append((later, _reclaim(bars, side, edge, later["end"])))
    return cycles


def _reclaim(bars: list[dict[str, Any]], side: str, edge: Decimal, after_ns: int) -> dict[str, Any] | None:
    for row in bars:
        if int(row["start"]) < int(after_ns):
            continue
        if side == "long" and row.get("H") is not None and row["H"] >= edge:
            return row
        if side == "short" and row.get("L") is not None and row["L"] <= edge:
            return row
    return None


def _touch_band(bars: list[dict[str, Any]], lo: Decimal, hi: Decimal) -> dict[str, Any] | None:
    for row in bars:
        if row.get("H") is None or row.get("L") is None:
            continue
        if row["L"] <= hi and row["H"] >= lo:
            return row
    return None


def _three_candle_ob(bars: list[dict[str, Any]], side: str, level: Decimal | None = None) -> dict[str, Any] | None:
    """TBR pp.27-28 / O056: C2 sweeps C1; C3 closes beyond C2's opposite extreme.

    When level is supplied, C2 must trade the location. Confirmation at a distant
    three-candle structure is not the source signature.
    """
    rows = [row for row in bars if row.get("C") is not None and row.get("H") is not None and row.get("L") is not None]
    for first, second, third in zip(rows, rows[1:], rows[2:]):
        if not (first["end"] <= second["start"] and second["end"] <= third["start"]):
            continue
        if level is not None and not (second["L"] <= level <= second["H"]):
            continue
        if side == "long":
            swept = second["L"] < first["L"]
            closed = third["C"] > second["H"]
            stop = second["L"] - TICK
        else:
            swept = second["H"] > first["H"]
            closed = third["C"] < second["L"]
            stop = second["H"] + TICK
        if swept and closed:
            return {"ok": True, "at": third["known_at"], "entry": third["C"], "stop": stop, "band": [str(second["L"]), str(second["H"])]}
    return None


def _rejection_block(bars: list[dict[str, Any]], side: str, level: Decimal | None = None) -> dict[str, Any] | None:
    """TBR p.29: rejection wick on the sweep candle; next candle closes beyond it.

    Timeframes are 2/3/5 minutes (TBR p.27). The wick must be the larger part of
    the candle so a one-tick tail is not a rejection block.
    """
    rows = [
        row
        for row in bars
        if row.get("O") is not None and row.get("C") is not None and row.get("H") is not None and row.get("L") is not None
    ]
    for sweep, close in zip(rows, rows[1:]):
        if sweep["end"] > close["start"]:
            continue
        if level is not None and not (sweep["L"] <= level <= sweep["H"]):
            continue
        body_lo = min(sweep["O"], sweep["C"])
        body_hi = max(sweep["O"], sweep["C"])
        body = body_hi - body_lo
        if side == "long":
            wick_w = body_lo - sweep["L"]
            closed = close["C"] > sweep["H"]
            band = [sweep["L"], body_lo]
        else:
            wick_w = sweep["H"] - body_hi
            closed = close["C"] < sweep["L"]
            band = [body_hi, sweep["H"]]
        if wick_w > body and closed:
            return {"ok": True, "at": close["known_at"], "band": [str(band[0]), str(band[1])]}
    return None


def _confirm_pack(
    market,
    start_ns: int,
    side: str,
    level: Decimal | None = None,
    horizon_min: int = 15,
    end_ns: int | None = None,
) -> dict[str, Any]:
    """F11: 2/3/5-minute full-C2 OB or rejection-block, each computed from bars."""
    close_ns = int(end_ns) if end_ns is not None else int(start_ns) + horizon_min * NS_MINUTE
    pack: dict[str, Any] = {"ob_2m": None, "ob_3m": None, "ob_5m": None, "rejection_block": None, "at": None}
    rb_seen = False
    rb_hit = False
    for seconds, key in ((120, "ob_2m"), (180, "ob_3m"), (300, "ob_5m")):
        rows = [row for row in _bars(market, int(start_ns), close_ns, seconds) if row["start"] >= int(start_ns)]
        complete = [row for row in rows if row.get("C") is not None and row.get("H") is not None and row.get("L") is not None]
        if len(complete) < 3:
            pack[key] = None
        else:
            found = _three_candle_ob(rows, side, level=level)
            pack[key] = found is not None
            if found is not None:
                pack["at"] = found["at"]
        if len(complete) >= 2:
            rb_seen = True
            found_rb = _rejection_block(rows, side, level=level)
            if found_rb is not None:
                rb_hit = True
                if pack["at"] is None:
                    pack["at"] = found_rb["at"]
    pack["rejection_block"] = True if rb_hit else (False if rb_seen else None)
    return pack


def _f11_verdict(pack: Mapping[str, Any]) -> str:
    flags = [pack.get(key) for key in ("ob_2m", "ob_3m", "ob_5m", "rejection_block")]
    if any(flag is True for flag in flags):
        return "pass"
    if all(flag is None for flag in flags):
        return "unknown"
    return "fail"


def _contact_kind(bar: Mapping[str, Any], level: Decimal, side: str) -> str | None:
    high, low = bar.get("H"), bar.get("L")
    if high is None or low is None:
        return None
    if low <= level <= high:
        if side == "long" and low < level:
            return "sweep"
        if side == "short" and high > level:
            return "sweep"
        return "touch"
    return None


def _overnight_span(market) -> dict[str, Any] | None:
    try:
        start = _at(market, "18:00", offset=-1)
    except Exception:
        return None
    end = _at(market, "09:30")
    bars = _cutoff(_bars(market, start, end, 60), end)
    return _span(bars, known_at=end)


def _purge_state(market, prior: Mapping[str, Any] | None) -> dict[str, Any]:
    overnight = _overnight_span(market)
    if overnight is None or not prior:
        return {"available": False, "purged_high": None, "purged_low": None, "compressed": None}
    pdh, pdl = _d(prior.get("high")), _d(prior.get("low"))
    prior_width = None if pdh is None or pdl is None else pdh - pdl
    width = overnight["high"] - overnight["low"]
    return {
        "available": True,
        "purged_high": None if pdh is None else overnight["high"] > pdh,
        "purged_low": None if pdl is None else overnight["low"] < pdl,
        "compressed": None if prior_width is None else width < prior_width,
        "overnight_high": str(overnight["high"]),
        "overnight_low": str(overnight["low"]),
        "overnight_width": str(width),
    }


def _context_sides(branch: str, label: str | None, purge: Mapping[str, Any]) -> tuple[str, ...]:
    """RR-02: enumerate both sides, keep the side the branch context permits."""
    if branch == "internal_rotation":
        return ("long", "short") if label == "inside_value" else ()
    if branch == "single_extended":
        if label in {"below_pdl", "below_val"}:
            return ("short",)
        if label in {"above_pdh", "above_vah"}:
            return ("long",)
        return ()
    if branch == "single_purged":
        if label not in {"below_val", "below_pdl"}:
            return ()
        if not purge.get("available"):
            return ()
        sides: list[str] = []
        if purge.get("purged_low") is True:
            sides.append("short")
        if purge.get("purged_high") is True:
            sides.append("long")
        return tuple(sides)
    return ("long", "short")


def _absorption(bar: Mapping[str, Any], avg_volume: Decimal | None) -> bool | None:
    open_, high, low, close = bar.get("O"), bar.get("H"), bar.get("L"), bar.get("C")
    if None in (open_, high, low, close):
        return None
    span = high - low
    if span <= 0:
        span = TICK
    body = abs(close - open_) / span
    vol_ok = True if avg_volume is None else Decimal(str(bar.get("volume") or 0)) >= Decimal("1.5") * avg_volume
    return body <= Decimal("0.6") and vol_ok


def _avg_volume(bars: list[dict[str, Any]], before_ns: int, n: int = 14) -> Decimal | None:
    prior = [row for row in bars if row["end"] <= before_ns]
    if len(prior) < n:
        return None
    window = prior[-n:]
    total = sum(Decimal(str(row.get("volume") or 0)) for row in window)
    return total / Decimal(n)


def _open_location(open_px: Decimal | None, prior: Mapping[str, Any] | None) -> str | None:
    if open_px is None or not prior:
        return None
    pdh, pdl = _d(prior.get("high")), _d(prior.get("low"))
    vah, val = _d(prior.get("vah")), _d(prior.get("val"))
    if pdl is not None and open_px < pdl:
        return "below_pdl"
    if val is not None and open_px < val:
        return "below_val"
    if val is not None and vah is not None and val <= open_px <= vah:
        return "inside_value"
    if pdh is not None and open_px > pdh:
        return "above_pdh"
    if vah is not None and open_px > vah:
        return "above_vah"
    if pdl is not None and pdh is not None and pdl <= open_px <= pdh:
        return "inside_value"
    return None


_PRIOR_CACHE: dict[str, dict[str, Any] | None] = {}


def _prior_rth(market) -> dict[str, Any] | None:
    injected = getattr(market, "prior_rth", None)
    if injected:
        return dict(injected)
    if hasattr(market, "prior"):
        try:
            payload = market.prior("day")
        except Exception:
            payload = None
        rng = (payload or {}).get("range") if isinstance(payload, Mapping) else None
        if rng:
            return {"high": rng.get("high"), "low": rng.get("low"), "known_at": rng.get("known_at")}
    day = _as_day(market)
    if day is None:
        return None
    key = day.isoformat()
    if key in _PRIOR_CACHE:
        return _PRIOR_CACHE[key]
    result = None
    try:
        from trading_research.research.rule_discovery.source_adapters.common import load_source_market

        hist = load_source_market(key)
        payload = hist.prior("day")
        rng = (payload or {}).get("range") if isinstance(payload, Mapping) else None
        if rng:
            result = {"high": rng.get("high"), "low": rng.get("low"), "known_at": rng.get("known_at")}
    except Exception:
        result = None
    _PRIOR_CACHE[key] = result
    return result


def _cash_open(market) -> tuple[Decimal | None, int | None]:
    rows = _bars(market, _at(market, "09:30"), _at(market, "09:31"), 60)
    if not rows:
        return None, None
    return rows[0].get("O"), rows[0].get("known_at")


def _context_label(market) -> tuple[str | None, list[str]]:
    unknown: list[str] = []
    open_px, at_ns = _cash_open(market)
    prior = _prior_rth(market)
    if open_px is None:
        unknown.append("rth_open")
    if prior is None:
        unknown.append("prior_rth")
    elif prior.get("val") is None or prior.get("vah") is None:
        unknown.append("prior_value")
    label = _open_location(open_px, prior)
    return label, unknown


def _stage(name: str, verdict: str, at_ns: int | None, **operands: Any) -> dict[str, Any]:
    return {"stage": name, "verdict": verdict, "at_ns": at_ns, "operands": operands}


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


def funnel_stage_counts(episodes: list[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    """Cascade pass along STAGE_ORDER. A fail or unknown stops later pass counts.

    Only stages present on every episode of the branch are kept, so an optional
    stage (confirmation when no OB, objective when no printed pivot) is omitted
    rather than sitting at zero between live stages.
    """
    if not episodes:
        return {}
    shared: set[str] | None = None
    parsed: list[dict[str, Mapping[str, Any]]] = []
    for episode in episodes:
        by_name = {str(stage.get("stage")): stage for stage in episode.get("stages") or [] if stage.get("stage") in STAGE_ORDER}
        names = set(by_name)
        shared = names if shared is None else shared & names
        parsed.append(by_name)
    order = [name for name in STAGE_ORDER if name in (shared or set())]
    counts = {name: {"pass": 0, "fail": 0, "unknown": 0} for name in order}
    for by_name in parsed:
        alive = True
        for name in order:
            if not alive:
                break
            verdict = str(by_name[name].get("verdict") or "unknown")
            if verdict not in counts[name]:
                counts[name][verdict] = 0
            counts[name][verdict] += 1
            if verdict != "pass":
                alive = False
    return {
        name: counts[name]
        for name in order
        if counts[name]["pass"] or counts[name]["fail"] or counts[name]["unknown"]
    }


def _file_line(fn) -> str:
    return f"source_adapters/jumbo.py:{inspect.getsourcelines(fn)[1]}"


_RULES_CACHE: list[dict[str, Any]] | None = None


def rules_payload() -> list[dict[str, Any]]:
    global _RULES_CACHE
    if _RULES_CACHE is not None:
        return list(_RULES_CACHE)
    impl = {
        "RR-01-extension-band-1.33-1.66": extension_reaction_bands,
        "RR-01-OD-near-band-0.33-0.66": mean_reversal_bands,
        "RR-06-projection-ladder": projection_ladder,
        "RR-02-eq-both-sides-context-bound": scan_b02,
        "RR-03-sweep-from-09:00": scan_b02,
        "RR-04-london-02:00-03:00": scan_b02,
        "F11-confirm-any-2-3-5-or-rejection": scan_b02,
        "RR-05-pzone-anchors": scan_b02,
        "RR-06-reclaim-entry": scan_b02,
        "RR-07-OD-sessionstat-60": scan_b02,
        "RR-08-open-location-at-09:30": scan_b02,
        "RR-09-published-statistics": compute_published_statistics,
        "F08-single-extended-reduced-after-10:00": scan_b02,
        "F11-confirm-3m-ob-baseline": scan_b02,
        "F12-candidate-references-unchanged": scan_b02,
        "F17-pzone-generator-unknown": scan_b02,
        "F18-ny-clock-ET": scan_b02,
        "F19-chart-clocks-UK-UTC": scan_b02,
    }
    rows = []
    for rule_id, meta in RULES.items():
        fn = impl.get(rule_id, scan_b02)
        rows.append(
            {
                "rule_id": rule_id,
                "kind": meta["kind"],
                "source": meta["source"],
                "finding": meta.get("finding"),
                "file_line": _file_line(fn),
                **({"parameters": meta["parameters"]} if "parameters" in meta else {}),
            }
        )
    _RULES_CACHE = rows
    return list(rows)


def _episode(
    *,
    branch: str,
    side: str,
    day: date | None,
    verdict: str,
    failed: list[str],
    unknown: list[str],
    values: dict[str, Any],
    geometry: dict[str, Any],
    stages: list[dict[str, Any]],
    decision_at: int | None,
) -> dict[str, Any]:
    status = {"pass": "setup", "fail": "no_setup", "unknown": "data_unavailable"}[verdict]
    ordered = [row for name in STAGE_ORDER for row in stages if row["stage"] == name]
    return {
        "schema": "phase1-historical-episode-v2",
        "candidate_id": f"b02:{FAMILY}:{branch}:{side}:{day}:{decision_at}",
        "method": FAMILY,
        "branch": branch,
        "side": side,
        "session_date": None if day is None else day.isoformat(),
        "research_verdict": verdict,
        "failed": list(failed),
        "unknown": list(unknown),
        "values": values,
        "geometry": geometry,
        "stages": ordered,
        "rules": rules_payload(),
        "decision_at": decision_at,
        "strategy_assessment": {"status": status},
    }


def _document(day: date | None, branch: str, episodes: list[dict[str, Any]], omissions: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"pass": 0, "fail": 0, "unknown": 0}
    for episode in episodes:
        counts[episode["research_verdict"]] += 1
    return {
        "schema_version": "research-family-b02-scan-v1",
        "baseline_version": "B0.2",
        "family": FAMILY,
        "branch": branch,
        "session_date": None if day is None else day.isoformat(),
        "clock_zone": "America/New_York",
        "chart_clock_notes": {"ninjatrader_2026": "UK local", "ticket_2025-01-28": "UTC", "source_prose": "ET"},
        "episodes": episodes,
        "omissions": omissions,
        "rules": rules_payload(),
        "n": counts["pass"] + counts["fail"],
        "p": counts["pass"],
        "f": counts["fail"],
        "u": counts["unknown"],
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


def _ny_range(market) -> dict[str, Any] | None:
    close = _at(market, "09:00")
    bars = _cutoff(_bars(market, _at(market, "06:00"), close, 60), close)
    return _span(bars, known_at=close)


def _london_range(market) -> dict[str, Any] | None:
    close = _at(market, "03:00")
    bars = _cutoff(_bars(market, _at(market, "02:00"), close, 60), close)
    return _span(bars, known_at=close)


def _sessionstat_box(market) -> dict[str, Any] | None:
    injected = getattr(market, "sessionstat_box", None)
    if injected:
        return dict(injected)
    return None


def _verdict(failed: list[str], unknown: list[str]) -> str:
    if failed:
        return "fail"
    if unknown:
        return "unknown"
    return "pass"


def _scan_judas_reversal(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    day = _as_day(market)
    formation = _ny_range(market)
    formation = enumeration_point(
        "references", formation, family="JJ-TBR", branch="judas_reversal", market=market
    )
    if formation is None:
        return [], [{"reason": "formation_has_no_observed_executions"}]
    high, low = formation["high"], formation["low"]
    width = high - low
    if width <= 0:
        return [], [{"reason": "nonpositive_formation_width"}]
    label, context_unknown = _context_label(market)
    clocks = enumeration_point(
        "window",
        {
            "sweep_lo": _at(market, "09:00"),
            "sweep_hi": _at(market, "10:00"),
            "reclaim_lo": _at(market, "09:00"),
            "reclaim_hi": _at(market, "11:00"),
            "modal_lo": _at(market, "09:40"),
            "modal_hi": _at(market, "09:50"),
            "confirm_lo": _at(market, "09:40"),
            "confirm_hi": _at(market, "10:10"),
        },
        family="JJ-TBR",
        branch="judas_reversal",
        market=market,
    )
    sweep_bars = _bars(market, int(clocks["sweep_lo"]), int(clocks["sweep_hi"]), 60)
    reclaim_bars = _bars(market, int(clocks["reclaim_lo"]), int(clocks["reclaim_hi"]), 60)
    modal_lo, modal_hi = int(clocks["modal_lo"]), int(clocks["modal_hi"])
    confirm_lo, confirm_hi = int(clocks["confirm_lo"]), int(clocks["confirm_hi"])
    episodes = []
    passed_session = False
    for side, edge, opposite in (("long", low, high), ("short", high, low)):
        for sweep, reclaim in _sweep_cycles(sweep_bars, side, edge, modal_lo, modal_hi):
            depth = (edge - sweep["L"]) if side == "long" else (sweep["H"] - edge)
            if reclaim is None:
                reclaim = _reclaim(reclaim_bars, side, edge, sweep["end"])
            confirm_start = max(int(sweep["end"]), confirm_lo)
            pack = _confirm_pack(
                market,
                confirm_start,
                side,
                level=sweep["L"] if side == "long" else sweep["H"],
                end_ns=confirm_hi,
            )
            f11 = _f11_verdict(pack)
            failed: list[str] = []
            unknown: list[str] = list(context_unknown)
            if reclaim is None:
                failed.append("edge_reclaimed")
                entry = None
                decision = sweep["known_at"]
            else:
                entry = reclaim.get("C") if reclaim.get("C") is not None else edge
                decision = reclaim["known_at"]
            action_cut = _cutoff(reclaim_bars, decision)
            if reclaim is not None and _reclaim(action_cut, side, edge, sweep["end"]) is None:
                failed.append("future_reclaim")
            if passed_session and "source_confirmation" not in failed and f11 == "pass" and reclaim is not None:
                failed.append("first_pass_already_taken")
                f11 = "fail"
            plus = edge + width * Decimal("0.5") if side == "long" else edge - width * Decimal("0.5")
            stop = (sweep["L"] - TICK) if side == "long" else (sweep["H"] + TICK)
            if f11 == "unknown":
                unknown.append("source_confirmation")
            elif f11 == "fail":
                failed.append("source_confirmation")
            verdict = _verdict(failed, [item for item in unknown if item == "source_confirmation"])
            if "edge_reclaimed" in failed:
                verdict = "fail"
            if "first_pass_already_taken" in failed:
                verdict = "fail"
            confirm_verdict = "fail" if reclaim is None or "first_pass_already_taken" in failed else f11
            stages = []
            if label is not None:
                stages.append(_stage("context", "pass", _at(market, "09:30"), open_location=label))
            stages.extend([
                _stage("reference", "pass", formation["known_at"], high=str(high), low=str(low), width=str(width), ladder=projection_ladder(high, low)),
                _stage("location", "pass", sweep["known_at"], edge=str(edge), mean_reversal=mean_reversal_bands(high, low)),
                _stage(
                    "trigger",
                    "pass",
                    sweep["known_at"],
                    sweep_at=sweep["start"],
                    sweep_depth=str(depth),
                    before_0930=sweep["start"] < _at(market, "09:30"),
                    in_modal_window=modal_lo <= sweep["start"] < modal_hi,
                    edge_reclaimed=reclaim is not None,
                ),
                _stage(
                    "confirmation",
                    confirm_verdict,
                    pack["at"] if pack["at"] is not None else (decision if reclaim is not None else sweep["known_at"]),
                    reclaim=reclaim is not None,
                    ob_3m=pack["ob_3m"],
                    ob_2m=pack["ob_2m"],
                    ob_5m=pack["ob_5m"],
                    rejection_block=pack["rejection_block"],
                ),
            ])
            if reclaim is not None and confirm_verdict == "pass":
                stages.append(_stage("risk", "pass" if stop is not None else "unknown", decision, stop=None if stop is None else str(stop)))
                stages.append(_stage("objective", "pass", decision, plus_0_5=str(plus), opposite_edge=str(opposite)))
            values = {
                "branch": "judas_reversal",
                "side": side,
                "open_location": label,
                "edge_swept": True,
                "sweep_at": sweep["start"],
                "sweep_depth": str(depth),
                "edge_reclaimed": reclaim is not None,
                "source_confirmation": None if f11 == "unknown" else f11 == "pass",
                "confirm_3m": pack["ob_3m"],
                "confirm_2m_od": pack["ob_2m"],
                "confirm_5m_od": pack["ob_5m"],
                "rejection_block": pack["rejection_block"],
                "modal_window": "09:40-09:50",
            }
            geometry = {
                "entry": None if entry is None else float(entry),
                "stop": None if stop is None else float(stop),
                "target": float(plus),
                "reference_level": float(edge),
                "sweep_depth": float(depth),
            }
            episodes.append(
                _episode(
                    branch="judas_reversal",
                    side=side,
                    day=day,
                    verdict=verdict,
                    failed=failed,
                    unknown=unknown,
                    values=values,
                    geometry=geometry,
                    stages=stages,
                    decision_at=decision,
                )
            )
            if verdict == "pass":
                passed_session = True
    return episodes, []


def _scan_judas_outbound(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    day = _as_day(market)
    formation = _ny_range(market)
    if formation is None:
        return [], [{"reason": "formation_has_no_observed_executions"}]
    high, low = formation["high"], formation["low"]
    width = high - low
    open_px, open_at = _cash_open(market)
    rows = _bars(market, _at(market, "09:30"), _at(market, "09:40"), 60)
    if not rows or open_px is None:
        return [], [{"reason": "opening_unknown", "operand": "rth_open"}]
    first = rows[0]
    episodes = []
    for side, edge in (("long", low), ("short", high)):
        swept = (side == "long" and first.get("L") is not None and first["L"] < edge) or (
            side == "short" and first.get("H") is not None and first["H"] > edge
        )
        if not swept and open_px == edge:
            swept = True
        if not swept:
            continue
        target = high + width * Decimal("0.5") if side == "long" else low - width * Decimal("0.5")
        stop = (low - TICK) if side == "long" else (high + TICK)
        decision = first["known_at"]
        at_open = int(first["start"]) == int(_at(market, "09:30"))
        depth = (edge - first["L"]) if side == "long" and first.get("L") is not None else (
            (first["H"] - edge) if side == "short" and first.get("H") is not None else None
        )
        pack = _confirm_pack(market, first["end"], side, level=edge, horizon_min=10)
        f11 = _f11_verdict(pack)
        failed: list[str] = []
        unknown: list[str] = []
        if f11 == "fail":
            failed.append("source_confirmation")
        elif f11 == "unknown":
            unknown.append("source_confirmation")
        verdict = _verdict(failed, unknown)
        stages = [
            _stage("context", "pass" if at_open else "fail", _at(market, "09:30"), at_rth_open=at_open, open_px=None if open_px is None else str(open_px)),
            _stage("reference", "pass", formation["known_at"], high=str(high), low=str(low)),
            _stage("trigger", "pass", first["start"], opening_sweep=True, sweep_depth=None if depth is None else str(depth)),
            _stage(
                "confirmation",
                f11,
                pack["at"] if pack["at"] is not None else decision,
                ob_2m=pack["ob_2m"],
                ob_3m=pack["ob_3m"],
                ob_5m=pack["ob_5m"],
                rejection_block=pack["rejection_block"],
            ),
        ]
        if not at_open:
            failed.append("at_rth_open")
            verdict = "fail"
        if verdict == "pass":
            stages.append(_stage("risk", "pass", decision, stop=str(stop), expiry_ns=int(_at(market, "09:40"))))
            stages.append(_stage("objective", "pass", decision, plus_0_5=str(target)))
        episodes.append(
            _episode(
                branch="judas_outbound",
                side=side,
                day=day,
                verdict=verdict,
                failed=failed,
                unknown=unknown,
                values={"branch": "judas_outbound", "side": side, "at_rth_open": at_open, "exit_window_recorded": True},
                geometry={"entry": float(open_px), "stop": float(stop), "target": float(target), "reference_level": float(edge), "sweep_depth": None if depth is None else float(depth)},
                stages=stages,
                decision_at=decision,
            )
        )
    return episodes, []


def _scan_extension_reaction(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    day = _as_day(market)
    formation = _ny_range(market)
    if formation is None:
        return [], [{"reason": "formation_has_no_observed_executions"}]
    high, low = formation["high"], formation["low"]
    bands = extension_reaction_bands(high, low)
    if not bands.get("available"):
        return [], [{"reason": "extension_band_unavailable", "detail": bands.get("reason")}]
    action = _bars(market, _at(market, "10:00"), _at(market, "16:00"), 60)
    box = _sessionstat_box(market)
    episodes = []
    for side, band in (("short", bands["upper"]), ("long", bands["lower"])):
        touch = _touch_band(action, band[0], band[1])
        if touch is None:
            continue
        decision = touch["known_at"]
        if int(touch["known_at"]) > decision:
            continue
        coincidence = None
        unknown: list[str] = []
        if box is None:
            unknown.append("sessionstat_box")
        else:
            blo, bhi = _d(box.get("low")), _d(box.get("high"))
            coincidence = blo is not None and bhi is not None and not (band[1] < blo or band[0] > bhi)
        entry = touch.get("C")
        stop = (touch["L"] - TICK) if side == "long" else (touch["H"] + TICK)
        target = low if side == "long" else high
        pack = _confirm_pack(market, touch["end"], side, level=(band[0] + band[1]) / 2, horizon_min=10)
        f11 = _f11_verdict(pack)
        failed: list[str] = []
        if f11 == "fail":
            failed.append("source_confirmation")
        elif f11 == "unknown":
            unknown.append("source_confirmation")
        range_frozen = formation["known_at"] <= _at(market, "09:00")
        after_1000 = touch["start"] >= _at(market, "10:00")
        stages = [
            _stage("context", "pass" if range_frozen else "fail", formation["known_at"], range_frozen=range_frozen, open_location=None),
            _stage("reference", "pass", formation["known_at"], high=str(high), low=str(low), ladder=projection_ladder(high, low)),
            _stage("location", "pass", formation["known_at"], band=[str(band[0]), str(band[1])], sessionstat_coincidence=coincidence),
            _stage("trigger", "pass" if after_1000 else "fail", touch["start"], after_1000=after_1000, kind="touch"),
            _stage(
                "confirmation",
                f11,
                pack["at"] if pack["at"] is not None else decision,
                ob_2m=pack["ob_2m"],
                ob_3m=pack["ob_3m"],
                ob_5m=pack["ob_5m"],
                rejection_block=pack["rejection_block"],
            ),
        ]
        if f11 == "pass" and not failed:
            stages.append(_stage("risk", "pass", decision, stop=str(stop)))
            stages.append(_stage("objective", "pass", decision, remaining_draw=str(target)))
        episodes.append(
            _episode(
                branch="extension_reaction",
                side=side,
                day=day,
                verdict=_verdict(failed, [item for item in unknown if item == "source_confirmation"]),
                failed=failed,
                unknown=unknown,
                values={
                    "branch": "extension_reaction",
                    "side": side,
                    "touch_in_source_extension_area": True,
                    "sessionstat_coincidence": coincidence,
                    "od_near_band": mean_reversal_bands(high, low),
                },
                geometry={
                    "entry": None if entry is None else float(entry),
                    "stop": float(stop),
                    "target": float(target),
                    "reference_level": float((band[0] + band[1]) / 2),
                    "sweep_depth": None,
                },
                stages=stages,
                decision_at=decision,
            )
        )
    return episodes, []


def _scan_other_session(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    day = _as_day(market)
    formation = _london_range(market)
    formation = enumeration_point("references", formation, family="JJ-TBR", branch="other_session", market=market)
    if formation is None:
        return [], [{"reason": "london_box_unobserved"}]
    high, low = formation["high"], formation["low"]
    width = high - low
    loc = quadrant_locations(low, high, "long")
    _clocks = enumeration_point(
        "window",
        {"begin": _at(market, "03:00"), "end": _at(market, "06:00")},
        family="JJ-TBR", branch="other_session", market=market, reference=formation,
    )
    action = _bars(market, int(_clocks["begin"]), int(_clocks["end"]), 60)
    bands = extension_reaction_bands(high, low)
    plus_half = high + width * Decimal("0.5")
    minus_half = low - width * Decimal("0.5")
    levels: list[tuple[str, Decimal, Decimal, str]] = [
        ("long", loc["q1"], loc["q1"], "q1"),
        ("long", loc["eq"], loc["eq"], "eq"),
        ("long", loc["q3"], loc["q3"], "q3"),
        ("long", low, low, "box_low"),
        ("long", minus_half, minus_half, "minus_0_5"),
        ("short", loc["q1"], loc["q1"], "q1"),
        ("short", loc["eq"], loc["eq"], "eq"),
        ("short", loc["q3"], loc["q3"], "q3"),
        ("short", high, high, "box_high"),
        ("short", plus_half, plus_half, "plus_0_5"),
    ]
    if bands.get("available"):
        levels.extend(
            [
                ("long", bands["lower"][0], bands["lower"][1], "ext"),
                ("short", bands["upper"][0], bands["upper"][1], "ext"),
            ]
        )
    box_known = formation.get("high") is not None and formation.get("low") is not None
    raid_bars = _bars(market, _at(market, "02:00"), _at(market, "06:00"), 60)
    low_raided = any(row.get("L") is not None and row["L"] < low for row in raid_bars)
    high_raided = any(row.get("H") is not None and row["H"] > high for row in raid_bars)
    episodes = []
    passed_side: set[str] = set()
    seen: set[tuple[str, str]] = set()
    for side, lo, hi, kind in levels:
        key = (side, kind)
        if key in seen:
            continue
        touch = _touch_band(action, lo, hi)
        if touch is None:
            continue
        seen.add(key)
        level = lo if side == "long" else hi
        kind_at = _contact_kind(touch, lo if lo == hi else (lo if side == "long" else hi), side)
        if kind != "ext" and kind_at is None:
            continue
        if kind == "ext":
            far = bands["lower"][0] if side == "long" else bands["upper"][1]
            kind_at = _contact_kind(touch, far, side) or "touch"
        plus = plus_half if side == "long" else minus_half
        stop = (touch["L"] - TICK) if side == "long" else (touch["H"] + TICK)
        decision = touch["known_at"]
        pack = _confirm_pack(market, touch["end"], side, level=level, horizon_min=10)
        f11 = _f11_verdict(pack)
        if pack.get("ob_3m") is not True:
            f11 = "unknown" if pack.get("ob_3m") is None and f11 == "unknown" else "fail"
        failed: list[str] = []
        unknown: list[str] = []
        trigger_ok = kind_at == "sweep"
        if not trigger_ok:
            failed.append("sweep")
        raided = low_raided if side == "long" else high_raided
        if not raided:
            failed.append("box_edge_swept")
            trigger_ok = False
        if f11 == "fail":
            failed.append("source_confirmation")
        elif f11 == "unknown":
            unknown.append("source_confirmation")
        if side in passed_side and not failed:
            failed.append("first_pass_already_taken")
            if f11 == "pass":
                f11 = "fail"
        verdict = _verdict(failed, unknown)
        if verdict == "pass":
            passed_side.add(side)
        depth = None
        if kind_at == "sweep":
            depth = (level - touch["L"]) if side == "long" else (touch["H"] - level)
        stages = [
            _stage(
                "context",
                "pass" if box_known else "unknown",
                formation["known_at"],
                box_observed=box_known,
                clock="02:00-03:00",
                box_low_swept=low_raided,
                box_high_swept=high_raided,
            ),
            _stage("reference", "pass", formation["known_at"], high=str(high), low=str(low), box="02:00-03:00"),
            _stage("location", "pass", touch["known_at"], kind=kind, level=str(level)),
            _stage(
                "trigger",
                "pass" if trigger_ok else "fail",
                touch["start"],
                kind=kind_at,
                window_start=_at(market, "03:00"),
                window_end=_at(market, "06:00"),
                sweep_depth=None if depth is None else str(depth),
                box_edge_swept=raided,
            ),
            _stage(
                "confirmation",
                f11,
                pack["at"] if pack["at"] is not None else decision,
                ob_2m=pack["ob_2m"],
                ob_3m=pack["ob_3m"],
                ob_5m=pack["ob_5m"],
                rejection_block=pack["rejection_block"],
            ),
        ]
        if verdict == "pass":
            stages.append(_stage("risk", "pass", decision, stop=str(stop)))
            stages.append(_stage("objective", "pass", decision, plus_0_5=str(plus)))
        episodes.append(
            _episode(
                branch="other_session",
                side=side,
                day=day,
                verdict=verdict,
                failed=failed,
                unknown=unknown,
                values={"branch": "other_session", "side": side, "source_clock_verified": box_known, "location_kind": kind, "trigger_kind": kind_at},
                geometry={
                    "entry": None if touch.get("C") is None else float(touch["C"]),
                    "stop": float(stop),
                    "target": float(plus),
                    "reference_level": float(level if kind != "ext" else ((bands["lower"][0] + bands["lower"][1]) / 2 if side == "long" else (bands["upper"][0] + bands["upper"][1]) / 2)),
                    "sweep_depth": None if depth is None else float(depth),
                },
                stages=stages,
                decision_at=decision,
            )
        )
    return episodes, []


def _scan_pzone(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    day = _as_day(market)
    key = None if day is None else day.isoformat()
    boxes = PZONE_FIXTURES.get(key or "", [])
    if not boxes:
        return [], [{"reason": "pzone_generator_unknown", "operand": "source_zone_known", "kind": "external_operand"}]
    session_bars = _bars(market, _at(market, "02:00"), _at(market, "16:00"), 60)
    episodes = []
    omissions = [{"reason": "pzone_generator_unknown", "operand": "source_zone_known"}]
    for box in boxes:
        lo, hi = box["low"], box["high"]
        side = box.get("side") or "long"
        anchor = box["anchor"]
        action_start = _at(market, anchor)
        action_end = _at(market, "16:00") if anchor != "02:00" else _at(market, "06:00")
        window = [row for row in session_bars if action_start <= row["start"] < action_end]
        hit = None
        for row in window:
            inside = row.get("L") is not None and row.get("H") is not None and row["L"] <= hi and row["H"] >= lo
            if not inside:
                continue
            avg = _avg_volume(session_bars, row["start"])
            absorbed = _absorption(row, avg)
            if absorbed is None:
                hit = row
                absorbed_flag: bool | None = None
                break
            if absorbed:
                hit = row
                absorbed_flag = True
                break
        else:
            absorbed_flag = False
        if hit is None:
            continue
        decision = hit["known_at"]
        entry = hit.get("C")
        stop = (lo - TICK) if side == "long" else (hi + TICK)
        target = box.get("target")
        unknown = [] if absorbed_flag is True else ["absorption_print"]
        if target is None:
            unknown.append("three_day_pivot")
        failed = []
        verdict = "pass" if absorbed_flag is True else "unknown"
        stages = [
            _stage("reference", "pass", action_start, box=[str(lo), str(hi)], anchor=anchor, session_2_alt="09:50"),
            _stage("location", "pass", action_start, inside_box=True),
            _stage("trigger", "pass" if absorbed_flag else "unknown", hit["start"], absorption=absorbed_flag),
            _stage("confirmation", "pass" if absorbed_flag else "unknown", decision, proxy="absorption_zone_plus"),
            _stage("risk", "pass", decision, stop=str(stop)),
        ]
        if target is not None:
            stages.append(_stage("objective", "pass", decision, three_day_pivot=str(target)))
        episodes.append(
            _episode(
                branch="timed_pzone_reversal",
                side=side,
                day=day,
                verdict=verdict,
                failed=failed,
                unknown=unknown,
                values={
                    "branch": "timed_pzone_reversal",
                    "side": side,
                    "source_zone_known": True,
                    "source_zone_kind": "author_printed_fixture",
                    "absorption": absorbed_flag,
                },
                geometry={
                    "entry": None if entry is None else float(entry),
                    "stop": float(stop),
                    "target": None if target is None else float(target),
                    "reference_level": float((lo + hi) / 2),
                    "sweep_depth": None,
                },
                stages=stages,
                decision_at=decision,
            )
        )
    return episodes, omissions


def _scan_eq_branch(market, branch: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    day = _as_day(market)
    formation = _ny_range(market)
    formation = enumeration_point("references", formation, family="JJ-TBR", branch=branch, market=market)
    if formation is None:
        return [], [{"reason": "formation_has_no_observed_executions"}]
    high, low = formation["high"], formation["low"]
    loc = quadrant_locations(low, high, "long")
    label, context_unknown = _context_label(market)
    prior = _prior_rth(market)
    purge = _purge_state(market, prior)
    allowed = _context_sides(branch, label, purge)
    if not allowed:
        return [], [{"reason": "no_qualifying_context", "branch": branch, "open_location": label, "purge": {k: purge.get(k) for k in ("purged_high", "purged_low", "compressed")}}]
    start = _at(market, "09:00")
    end = _at(market, "16:00")
    if branch == "single_purged":
        start = _at(market, "09:40")
        end = _at(market, "09:50")
    _clocks = enumeration_point(
        "window", {"begin": start, "end": end}, family="JJ-TBR", branch=branch, market=market, reference=formation
    )
    start, end = int(_clocks["begin"]), int(_clocks["end"])
    action = _bars(market, start, end, 60)
    episodes = []
    contacts = (("eq", loc["eq"]),)
    if branch != "internal_rotation":
        contacts = (("eq", loc["eq"]), ("q1", loc["q1"]), ("q3", loc["q3"]))
    for kind, level in contacts:
        for side in ("long", "short"):
            if side not in allowed:
                continue
            touch = _touch_band(action, level, level)
            if touch is None:
                continue
            kind_at = _contact_kind(touch, level, side) or "touch"
            decision = touch["known_at"]
            reduced = branch == "single_extended" and touch["start"] >= _at(market, "10:00")
            pack = _confirm_pack(market, touch["end"], side, level=level, horizon_min=10)
            f11 = _f11_verdict(pack)
            failed: list[str] = []
            unknown = list(context_unknown)
            if branch == "internal_rotation" and kind_at != "sweep":
                failed.append("eq_sweep")
            if f11 == "fail":
                failed.append("source_confirmation")
            elif f11 == "unknown":
                unknown.append("source_confirmation")
            target = high if side == "long" else low
            stop = (touch["L"] - TICK) if side == "long" else (touch["H"] + TICK)
            verdict = _verdict(failed, [item for item in unknown if item == "source_confirmation"])
            loc_operands: dict[str, Any] = {"kind": kind, "level": str(level)}
            if branch == "internal_rotation":
                evr = EVRANGE_FIXTURES.get(day.isoformat() if day else "")
                if evr is None and day is not None and day > TAPE_LAST:
                    loc_operands["evrange"] = "data_unavailable"
            stages = [
                _stage(
                    "context",
                    "pass",
                    _at(market, "09:30"),
                    open_location=label,
                    selector=branch,
                    allowed_sides=list(allowed),
                    purged_high=purge.get("purged_high"),
                    purged_low=purge.get("purged_low"),
                    compressed=purge.get("compressed"),
                ),
                _stage("reference", "pass", formation["known_at"], high=str(high), low=str(low)),
                _stage("location", "pass", touch["known_at"], **loc_operands),
                _stage(
                    "trigger",
                    "fail" if "eq_sweep" in failed else "pass",
                    touch["start"],
                    kind=kind_at,
                    reduced_expectations=reduced if branch == "single_extended" else False,
                ),
                _stage(
                    "confirmation",
                    f11,
                    pack["at"] if pack["at"] is not None else decision,
                    ob_2m=pack["ob_2m"],
                    ob_3m=pack["ob_3m"],
                    ob_5m=pack["ob_5m"],
                    rejection_block=pack["rejection_block"],
                ),
            ]
            if verdict == "pass":
                stages.append(_stage("risk", "pass", decision, stop=str(stop)))
                stages.append(_stage("objective", "pass", decision, range_edge=str(target)))
            episodes.append(
                _episode(
                    branch=branch,
                    side=side,
                    day=day,
                    verdict=verdict,
                    failed=failed,
                    unknown=unknown,
                    values={
                        "branch": branch,
                        "side": side,
                        "open_location": label,
                        "reduced_expectations": reduced if branch == "single_extended" else False,
                        "entry_at_eq_or_quadrant": True,
                    },
                    geometry={
                        "entry": None if touch.get("C") is None else float(touch["C"]),
                        "stop": float(stop),
                        "target": float(target),
                        "reference_level": float(level),
                        "sweep_depth": None,
                    },
                    stages=stages,
                    decision_at=decision,
                )
            )
    return episodes, []


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


def _rec_branch(rec: Any) -> str | None:
    if rec is None:
        return None
    if isinstance(rec, str):
        return rec
    if isinstance(rec, Mapping):
        value = rec.get("branch") or rec.get("source_branch")
        return None if value is None else str(value)
    return None


def scan_b02(market, rec, *, overrides=None) -> dict[str, Any]:
    """Source-faithful B0.2 scan. Does not mutate B0 or B0.1 documents."""
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
        return finish(_document(day, branch or "all", [], [{"reason": "data_unavailable"}]))
    if day > TAPE_LAST:
        return finish(_document(day, branch or "all", [], [{"reason": "data_unavailable", "date": day.isoformat()}]))
    branches = BRANCHES if not branch else (branch,)
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
    return finish(_document(day, branch or "all", episodes, omissions))


def _example_levels(example: Mapping[str, Any]) -> list[float]:
    levels = example.get("levels") or {}
    out: list[float] = []
    for value in levels.values():
        if isinstance(value, (int, float, Decimal)):
            out.append(float(value))
        elif isinstance(value, list) and value and isinstance(value[0], (int, float, Decimal)):
            out.extend(float(item) for item in value if isinstance(item, (int, float, Decimal)))
        elif isinstance(value, Mapping):
            for inner in value.values():
                if isinstance(inner, (int, float, Decimal)):
                    out.append(float(inner))
    preferred = _author_level(example)
    if preferred is not None:
        out.append(preferred)
    return out


def _failing_from_episode(episode: Mapping[str, Any]) -> tuple[str | None, str | None]:
    failed = list(episode.get("failed") or [])
    if failed:
        return failed[0], next((str(row.get("stage")) for row in episode.get("stages") or [] if row.get("verdict") == "fail"), None)
    for row in episode.get("stages") or []:
        if row.get("verdict") in {"fail", "unknown"}:
            operands = row.get("operands") or {}
            name = next(iter(operands), None)
            return (None if name is None else str(name)), str(row.get("stage"))
    return None, None


def _author_level(example: Mapping[str, Any]) -> float | None:
    levels = example.get("levels") or {}
    expected = example.get("expected_detection") or {}
    side = str(expected.get("side") or "")
    branch = str(expected.get("branch") or "")
    if "extension" in branch:
        if "long" in side:
            for key in ("minus_1_66", "minus_1_33"):
                if isinstance(levels.get(key), (int, float, Decimal)):
                    return float(levels[key])
        else:
            for key in ("plus_1_66", "plus_1_33"):
                if isinstance(levels.get(key), (int, float, Decimal)):
                    return float(levels[key])
        band = levels.get("plus_1_33_1_66_band")
        if isinstance(band, list) and band and isinstance(band[0], (int, float, Decimal)):
            return float(sum(float(x) for x in band[:2]) / len(band[:2]))
    preferred = ("L", "minus_1_66", "minus_1_33", "R_lo") if "long" in side else ("H", "plus_1_66", "plus_1_33", "R_hi")
    for key in preferred + ("EQ", "H", "L"):
        value = levels.get(key)
        if isinstance(value, (int, float, Decimal)):
            return float(value)
    for value in levels.values():
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        if isinstance(value, list) and value and isinstance(value[0], (int, float, Decimal)):
            return float(value[0])
    return None


def _author_side(example: Mapping[str, Any]) -> str | None:
    side = (example.get("expected_detection") or {}).get("side")
    if side in {"long", "short"}:
        return side
    for action in example.get("actions") or []:
        if action.get("action") in {"buy", "sell"}:
            return "long" if action["action"] == "buy" else "short"
    if isinstance(side, str) and "long" in side:
        return "long"
    if isinstance(side, str) and "short" in side:
        return "short"
    return None


def _window_bounds(day: date, window: str | None) -> tuple[int, int] | None:
    if not window or "-" not in window:
        return None
    left, right = window.split("-", 1)
    try:
        sh, sm = [int(part) for part in left.strip().split(":")]
        eh, em = [int(part) for part in right.strip().split(":")]
    except ValueError:
        return None
    from trading_research.research.method_pack.clocks import et_ns

    return et_ns(day, sh, sm), et_ns(day, eh, em)


def _primary_branch(expected: str | None) -> str | None:
    if not expected:
        return None
    for name in BRANCHES:
        if name in expected:
            return name
    return None


def replay_example(market, example) -> dict[str, Any]:
    payload = dict(example or {})
    expected = payload.get("expected_detection") or {}
    day_text = payload.get("date")
    author_level = _author_level(payload)
    author_side = _author_side(payload)
    branch_expected = expected.get("branch") or ""
    result = {
        "id": payload.get("id"),
        "detected": None,
        "branch": _primary_branch(branch_expected) or branch_expected,
        "our_side": None,
        "our_level": None,
        "our_entry_ns": None,
        "author_level": author_level,
        "author_side": author_side,
        "divergence": "",
        "reached_location": False,
        "failing_operand": None,
        "failing_stage": None,
    }
    inside = payload.get("inside_tape", True)
    day = date.fromisoformat(day_text) if day_text else None
    if day is None and market is not None:
        day = _as_day(market)
    if (
        inside is False
        or (day is not None and (day < TAPE_FIRST or day > TAPE_LAST))
    ):
        result["detected"] = None
        result["divergence"] = OUTSIDE_TAPE
        result["failing_operand"] = "date"
        result["failing_stage"] = None
        return result
    if market is None or day is None:
        result["detected"] = None
        result["divergence"] = "data_unavailable"
        result["failing_operand"] = "market"
        return result
    rec_branch = _primary_branch(branch_expected)
    document = scan_b02(market, {"branch": rec_branch} if rec_branch else None)
    window = _window_bounds(day, expected.get("entry_window_et")) if day else None
    author_levels = _example_levels(payload)
    scored: list[tuple[int, dict[str, Any], str]] = []
    for episode in document.get("episodes") or []:
        if rec_branch and episode.get("branch") != rec_branch and rec_branch not in str(branch_expected):
            continue
        side_ok = author_side is None or episode.get("side") == author_side or author_side not in {"long", "short"}
        if not side_ok and "long then short" in str(expected.get("side")):
            side_ok = episode.get("side") in {"long", "short"}
        level = (episode.get("geometry") or {}).get("reference_level")
        level_ok = author_level is None or level is None or abs(Decimal(str(level)) - Decimal(str(author_level))) <= REPLAY_LEVEL_TOLERANCE
        entry_ns = episode.get("decision_at")
        window_ok = True if window is None or entry_ns is None else window[0] <= int(entry_ns) < window[1]
        loc_stage = next((row for row in episode.get("stages") or [] if row.get("stage") == "location"), None)
        loc_pass = loc_stage is not None and loc_stage.get("verdict") == "pass"
        loc_level_ok = False
        if level is not None and author_levels:
            loc_level_ok = any(abs(Decimal(str(level)) - Decimal(str(item))) <= REPLAY_LEVEL_TOLERANCE for item in author_levels)
        elif loc_pass:
            loc_level_ok = author_level is None
        if loc_pass and loc_level_ok:
            result["reached_location"] = True
        passed = episode.get("research_verdict") == "pass"
        score = int(passed) + int(side_ok) + int(level_ok) + int(window_ok)
        reason = "match"
        if not passed:
            reason = f"miss: verdict={episode.get('research_verdict')}"
        elif not side_ok:
            reason = f"miss: side {episode.get('side')} vs {author_side}"
        elif not level_ok:
            reason = f"miss: level {level} vs {author_level}"
        elif not window_ok:
            reason = "miss: entry_outside_window"
        scored.append((score, episode, reason))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        if any(row.get("reason") == "data_unavailable" for row in document.get("omissions") or []):
            result["detected"] = None
            result["divergence"] = "data_unavailable"
            result["failing_operand"] = "market"
        else:
            result["detected"] = False
            result["divergence"] = "miss"
            omit = (document.get("omissions") or [{}])[0]
            result["failing_operand"] = str(omit.get("reason") or "location")
            result["failing_stage"] = "location"
        return result
    score, best, reason = scored[0]
    result["our_side"] = best.get("side")
    result["our_level"] = (best.get("geometry") or {}).get("reference_level")
    result["our_entry_ns"] = best.get("decision_at")
    result["branch"] = best.get("branch") or result["branch"]
    result["detected"] = reason == "match"
    result["divergence"] = reason
    if reason != "match":
        operand, stage = _failing_from_episode(best)
        if reason.startswith("miss: level"):
            operand, stage = "reference_level", "location"
        elif reason.startswith("miss: side"):
            operand, stage = "side", "location"
        elif "entry_outside_window" in reason:
            operand, stage = "entry_window_et", "trigger"
        elif operand is None:
            operand, stage = "research_verdict", (stage or "confirmation")
        result["failing_operand"] = operand
        result["failing_stage"] = stage
        if best.get("failed"):
            result["divergence"] = f"{reason}; failed={best.get('failed')}"
    our_level = result.get("our_level")
    if payload.get("id") == "JJ-2025-09-09" and our_level is not None and author_level is not None:
        lo, hi = Decimal("23727.00"), Decimal("23743.50")
        mid = Decimal(str(our_level))
        if lo <= mid <= hi:
            note = (
                f"level-selection: our_level {our_level} is inside the RR-01 lower band "
                f"[{lo}, {hi}]; author_level {author_level} is the band far edge. Finding, not a rule change."
            )
            result["level_selection"] = note
            if "miss: level" in str(result["divergence"]):
                result["divergence"] = f"{result['divergence']}; {note}"
    return result


def compute_published_statistics(dates: list[str]) -> dict[str, Any]:
    source = {
        "extended_range_reversal_share": 0.8646,
        "reversal_modal_window": "09:40-09:50",
        "source_sentence_jr_p70": "An astonishing 86.46% of reversal of off the -0.5 stdv (exhaustion)",
        "capture_1_33": {"high": 0.892, "low": 0.656, "n": 3753},
        "capture_1_66": {"high": 0.924, "low": 0.668, "n": 3753},
        "first_hour_sweep": {
            "below_val_inside_range": {"n": 396, "high_only": 0.295, "low_only": 0.376, "both": 0.298, "one_side": 0.672},
            "below_val_and_pdl": {"n": 517, "high_only": 0.236, "low_only": 0.462, "both": 0.273, "one_side": 0.698},
        },
    }
    bins = [f"{hour:02d}:{minute:02d}" for hour in range(9, 12) for minute in (0, 10, 20, 30, 40, 50)]
    bin_counts = {key: 0 for key in bins}
    capture = {"n": 0, "high_133": 0, "low_133": 0, "high_166": 0, "low_166": 0}
    sweeps = {"n": 0, "high_only": 0, "low_only": 0, "both": 0, "one_side": 0, "by_open_location": {}}
    reversals = 0
    days_used = 0
    for item in dates:
        try:
            day = date.fromisoformat(item)
        except ValueError:
            continue
        if day > TAPE_LAST:
            continue
        market = None
        if hasattr(item, "completed_bars") or hasattr(item, "bars"):
            market = item
        else:
            try:
                from trading_research.research.rule_discovery.native import build_market_view

                market = build_market_view(item)
            except Exception:
                continue
        formation = _ny_range(market)
        if formation is None:
            continue
        days_used += 1
        high, low, width = formation["high"], formation["low"], formation["high"] - formation["low"]
        session = _bars(market, _at(market, "09:00"), _at(market, "16:00"), 60)
        if not session:
            continue
        session_high = max(row["H"] for row in session if row.get("H") is not None)
        session_low = min(row["L"] for row in session if row.get("L") is not None)
        capture["n"] += 1
        if session_high >= high + Decimal("1.33") * width:
            capture["high_133"] += 1
        if session_low <= low - Decimal("1.33") * width:
            capture["low_133"] += 1
        if session_high >= high + Decimal("1.66") * width:
            capture["high_166"] += 1
        if session_low <= low - Decimal("1.66") * width:
            capture["low_166"] += 1
        first_hour = [row for row in session if _at(market, "09:30") <= row["start"] < _at(market, "10:30")]
        took_h = any(row.get("H") is not None and row["H"] > high for row in first_hour)
        took_l = any(row.get("L") is not None and row["L"] < low for row in first_hour)
        sweeps["n"] += 1
        hour_row = classify_first_hour_sweep(took_h, took_l)
        for key in ("high_only", "low_only", "both", "one_side"):
            sweeps[key] += hour_row[key]
        label, _unknown = _context_label(market)
        loc_row = sweeps["by_open_location"].setdefault(
            label or "unknown", {"n": 0, "high_only": 0, "low_only": 0, "both": 0, "one_side": 0}
        )
        loc_row["n"] += 1
        for key in ("high_only", "low_only", "both", "one_side"):
            loc_row[key] += hour_row[key]
        exhaust_low = low - Decimal("0.5") * width
        exhaust_high = high + Decimal("0.5") * width
        sweep = _first_sweep(session, "long", low) or _first_sweep(session, "short", high)
        reclaim = None
        if sweep is not None:
            side = "long" if sweep.get("L") is not None and sweep["L"] < low else "short"
            edge = low if side == "long" else high
            reclaim = _reclaim(session, side, edge, sweep["end"])
            extreme = sweep["L"] if side == "long" else sweep["H"]
            if (side == "long" and extreme <= exhaust_low) or (side == "short" and extreme >= exhaust_high):
                reversals += 1
        if reclaim is not None:
            from trading_research.research.method_pack.clocks import ns_to_et

            stamp = ns_to_et(reclaim["start"])
            key = f"{stamp.hour:02d}:{(stamp.minute // 10) * 10:02d}"
            if key in bin_counts:
                bin_counts[key] += 1
    measured_share = None if days_used == 0 else reversals / days_used
    n_cap = capture["n"] or 1
    n_sw = sweeps["n"] or 1
    measured = {
        "n_days": days_used,
        "extended_range_reversal_share": measured_share,
        "reversal_bins_09:00-12:00": bin_counts,
        "capture_1_33": {"high": capture["high_133"] / n_cap, "low": capture["low_133"] / n_cap, "n": capture["n"]},
        "capture_1_66": {"high": capture["high_166"] / n_cap, "low": capture["low_166"] / n_cap, "n": capture["n"]},
        "first_hour_sweep": {
            "high_only": sweeps["high_only"] / n_sw,
            "low_only": sweeps["low_only"] / n_sw,
            "both": sweeps["both"] / n_sw,
            "one_side": sweeps["one_side"] / n_sw,
            "one_side_definition": "high_only + low_only (JR p.37; excludes both)",
            "n": sweeps["n"],
            "by_open_location": sweeps["by_open_location"],
        },
    }
    findings = []
    if measured_share is not None and abs(measured_share - source["extended_range_reversal_share"]) > 0.05:
        findings.append("extended_range_reversal_share differs from 86.46% on this sample")
    if abs(measured["capture_1_33"]["high"] - source["capture_1_33"]["high"]) > 0.05:
        findings.append("1.33 high capture differs from 89.2% on this sample")
    findings.append(
        "RR-09 BigTrades >=100 NY / >=75 London (JR p.50) and the JR pp.49-50 35% footprint transaction filter are deferred; they are two different flow views and neither is a labelled native-tape series"
    )
    return {"source": source, "measured": measured, "findings": findings, "sample": "engineering_slice_or_supplied_dates"}

