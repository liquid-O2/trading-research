"""Dated range, reference, and source-geometry objects for Phase 1.

The native producers consume only ``ResolvedMembers`` observations.  Recipe
helpers also accept explicit parent/source records for objects whose author
construction is unpublished; those paths retain the corresponding holes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence

from trading_research.research.method_pack.clocks import MINUTE_NS, ns_to_et
from trading_research.research.method_pack.contracts import OutputField
from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult


class GeometryError(ValueError):
    pass


@dataclass(frozen=True)
class RangeGeometry:
    range_id: str
    instrument_id: str | int
    source_clock_id: str
    formation_start: int
    formation_end: int
    known_at: int | None
    L: Decimal
    H: Decimal
    W: Decimal
    coverage_ok: bool | None
    member_ids: tuple[str, ...]
    parent_id: str | None = None


def _r(rid: str, value: dict[str, Any], *, holes: Sequence[str] = (), known_at: int | None = None,
       base_ok: bool | None = True, coverage_ok: bool | None = True,
       state: str | None = None, reason: str | None = None,
       parent_ids: Sequence[str] = (), evidence_ids: Sequence[str] = ()) -> RecipeResult:
    contact_known=value.pop("_selected_contact_known_at", "absent")
    if contact_known != "absent":
        known_at=max(known_at,contact_known) if type(known_at) is int and type(contact_known) is int else None
    schema=globals().get("OUTPUT_SCHEMAS",{}).get(rid,{})
    if state != "invalid":value={**{key:None for key,field in schema.items() if field.nullable},**value}
    return RecipeResult(rid, state or ("computed" if not holes else "hole"), value,
                        list(dict.fromkeys(holes)), known_at=known_at,
                        base_ok=base_ok, coverage_ok=coverage_ok, reason=reason,
                        parent_ids=list(parent_ids), evidence_ids=list(evidence_ids))


def _invalid(rid: str, message: str, field: str = "evidence") -> RecipeResult:
    return _r(rid, {}, holes=[f"HOLE:{rid}:{field}"], state="invalid",
              base_ok=False, coverage_ok=None, reason=message)


def _ns(value: Any, name: str) -> int:
    if type(value) is not int:
        raise GeometryError(f"{name} must be an integer event key")
    return value


def _d(value: Any, name: str) -> Decimal:
    result = dec(value)
    if result is None:
        raise GeometryError(f"{name} is required")
    return result


def _ordered(*values: int | None, strict: bool = True) -> bool | None:
    if any(value is None for value in values):
        return None
    pairs = zip(values, values[1:])
    return all(a < b if strict else a <= b for a, b in pairs)


def _relation(price: Decimal | None, lo: Decimal | None, hi: Decimal | None) -> str | None:
    if price is None or lo is None or hi is None:
        return None
    if lo > hi:
        raise GeometryError("reference bounds are reversed")
    if price == lo or price == hi:
        return "on_boundary"
    if price < lo:
        return "below"
    if price > hi:
        return "above"
    return "inside"


def _range_payload(rng: RangeGeometry) -> dict[str, Any]:
    return {
        "range_id": rng.range_id, "instrument_id": rng.instrument_id,
        "source_clock_id": rng.source_clock_id, "L": rng.L, "H": rng.H,
        "W": rng.W, "formation_start": rng.formation_start,
        "formation_end": rng.formation_end, "known_at": rng.known_at,
        "range_known_at": rng.known_at,
        "range_frozen": rng.coverage_ok is True and rng.known_at is not None,
        "coverage_ok": rng.coverage_ok, "member_ids": list(rng.member_ids),
        "parent_id": rng.parent_id,
    }


def build_native_range(config: Mapping[str, Any], resolved: Any) -> RangeGeometry:
    rows = resolved.rows()
    bars = [row for row in rows if row.get("start") is not None]
    events = [row for row in rows if row.get("event_ns") is not None and row.get("action") == "T"]
    if bars and events:
        raise GeometryError("range members cannot mix bars and executions")
    if not bars and not events:
        raise GeometryError("range has no price members")
    lows: list[Decimal] = []
    highs: list[Decimal] = []
    ids: list[str] = []
    availability: list[int | None] = [resolved.end_ns, resolved.known_at]
    coverage: bool | None = resolved.coverage_ok
    if bars:
        cursor = resolved.start_ns
        for row in sorted(bars, key=lambda item: item["start"]):
            if row["start"] < cursor:
                raise GeometryError("range bars overlap")
            if row.get("complete") is not True or row["start"] != cursor or row["end"] > resolved.end_ns:
                coverage = None
            if str(row.get("instrument_id")) != str(resolved.instrument_id):
                raise GeometryError("range member instrument mismatch")
            lows.append(_d(row.get("L"), "bar low")); highs.append(_d(row.get("H"), "bar high"))
            ids.append(str(row.get("bar_id")))
            cursor = max(cursor, row["end"])
            availability.append(row.get("known_at"))
        if cursor != resolved.end_ns:
            coverage = None
    else:
        for row in events:
            if not resolved.start_ns <= row["event_ns"] < resolved.end_ns:
                continue
            if str(row.get("instrument_id")) != str(resolved.instrument_id):
                raise GeometryError("range member instrument mismatch")
            price = _d(row.get("price"), "execution price")
            lows.append(price); highs.append(price); ids.append(str(row.get("event_id")))
            availability.append(row.get("known_at"))
    if not lows:
        raise GeometryError("range has no in-window price members")
    low, high = min(lows), max(highs)
    # A zero-width observed range is a valid empirical object.  Width-normalized
    # descendants reject it; the native observation itself is not fabricated
    # into an invalid identity.
    known = max(availability) if all(type(value) is int for value in availability) else None
    return RangeGeometry(
        str(config.get("range_id") or f"{resolved.instrument_id}:{resolved.start_ns}:{resolved.end_ns}"),
        resolved.instrument_id, str(config.get("source_clock_id") or "unverified"),
        resolved.start_ns, resolved.end_ns, known, low, high, high-low, coverage,
        tuple(ids), config.get("parent_id"),
    )


def _clock(rng: RangeGeometry) -> tuple[tuple[int, int], tuple[int, int]]:
    start, end = ns_to_et(rng.formation_start), ns_to_et(rng.formation_end)
    return (start.hour, start.minute), (end.hour, end.minute)


def native_o005(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        rng = build_native_range({**config, "source_clock_id": "JJ-TBR:06:00-09:00"}, resolved)
        if _clock(rng) != ((6, 0), (9, 0)):
            raise GeometryError("O005 requires the dated 06:00-09:00 ET clock")
        holes = []
        if rng.coverage_ok is not True: holes.append("HOLE:O005:coverage")
        if rng.known_at is None: holes.append("HOLE:O005:availability")
        return _r("O005", _range_payload(rng), holes=holes, known_at=rng.known_at,
                  coverage_ok=rng.coverage_ok,
                  evidence_ids=rng.member_ids)
    except GeometryError as exc:
        return _invalid("O005", str(exc), "complete_membership")


_MANUAL_CLOCKS = {((20, 0), (20, 30)), ((0, 0), (0, 30)), ((3, 0), (3, 30)),
                  ((9, 30), (10, 0)), ((10, 0), (10, 30)),
                  ((12, 0), (12, 30)), ((15, 0), (15, 30))}


def native_o006(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        qualifier = _optional_audited_source_values(config,
            ("source_clock_verified", "source_clock_id", "source_version"))
        verified = qualifier.get("source_clock_verified")
        clock_id = qualifier.get("source_clock_id") or "unverified"
        rng = build_native_range({**config, "source_clock_id": clock_id}, resolved)
        if qualifier.get("source_version") == "manual" and _clock(rng) not in _MANUAL_CLOCKS:
            raise GeometryError("window is not a printed manual formation clock")
        holes = []
        if rng.coverage_ok is not True: holes.append("HOLE:O006:coverage")
        if rng.known_at is None: holes.append("HOLE:O006:availability")
        if not verified: holes.append("HOLE:O006:source_clock")
        value = _range_payload(rng)
        value["source_clock_verified"] = verified
        return _r("O006", value, holes=holes, known_at=rng.known_at,
                  coverage_ok=rng.coverage_ok, evidence_ids=rng.member_ids)
    except GeometryError as exc:
        return _invalid("O006", str(exc), "source_clock")


def native_o011(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        rng = build_native_range(config, resolved)
        if config.get("source") == "sires" and _clock(rng) != ((18, 0), (9, 30)):
            raise GeometryError("Sires overnight must be 18:00-09:30 ET")
        if not config.get("window_id"):
            raise GeometryError("overnight window identity is required")
        holes = [] if rng.coverage_ok is True else ["HOLE:O011:coverage"]
        if rng.known_at is None: holes.append("HOLE:O011:availability")
        return _r("O011", {"on_high": rng.H, "on_low": rng.L, "on_width": rng.W,
            "window_id": config["window_id"], "known_at": rng.known_at,
            "formation_start": rng.formation_start, "formation_end": rng.formation_end,
            "instrument_id": rng.instrument_id, "coverage_ok": rng.coverage_ok,
            "member_ids": list(rng.member_ids)}, holes=holes, known_at=rng.known_at,
            coverage_ok=rng.coverage_ok,
            evidence_ids=rng.member_ids)
    except GeometryError as exc:
        return _invalid("O011", str(exc), "window")


def _native_range_alias(rid: str, config: Mapping[str, Any], resolved: Any,
                        *, clock: tuple[tuple[int, int], tuple[int, int]] | None = None) -> RecipeResult:
    try:
        rng = build_native_range(config, resolved)
        if clock is not None and _clock(rng) != clock:
            raise GeometryError(f"{rid} source clock mismatch")
        range_holes = []
        if rng.coverage_ok is not True: range_holes.append(f"HOLE:{rid}:coverage")
        if rng.known_at is None: range_holes.append(f"HOLE:{rid}:availability")
        if rid == "O020":
            qualifier = _optional_audited_source_values(config,
                ("rth_active_objectives", "chosen_draw", "current_direction"))
            context_holes = [f"HOLE:O020:{key}" for key in
                ("rth_active_objectives", "chosen_draw", "current_direction")
                if qualifier.get(key) is None]
            return _r(rid, {"prior_rth_high": rng.H, "prior_rth_low": rng.L,
                "prior_range_id": rng.range_id, "known_at": rng.known_at,
                "rth_active_objectives": list(qualifier.get("rth_active_objectives") or ()),
                "chosen_draw": qualifier.get("chosen_draw"),
                "current_direction": qualifier.get("current_direction"),
                "coverage_ok": rng.coverage_ok}, holes=[*range_holes, *context_holes], known_at=rng.known_at,
                coverage_ok=rng.coverage_ok, evidence_ids=rng.member_ids)
        if rid == "O025":
            qualifier = _optional_audited_source_values(config,
                ("source_clock_verified", "subsequent_mid_retrace"))
            if qualifier.get("source_clock_verified") is not True:
                return _r(rid, {"or_mid": (rng.H+rng.L)/2, "or_high": rng.H,
                    "or_low": rng.L, "or_id": rng.range_id, "or_known": None,
                    "subsequent_mid_retrace": qualifier.get("subsequent_mid_retrace"), "known_at": rng.known_at},
                    holes=["HOLE:O025:or_clock"], known_at=rng.known_at, coverage_ok=None)
            return _r(rid, {"or_mid": (rng.H+rng.L)/2, "or_high": rng.H,
                "or_low": rng.L, "or_id": rng.range_id, "or_known": True,
                "subsequent_mid_retrace": qualifier.get("subsequent_mid_retrace"),
                "known_at": rng.known_at}, holes=range_holes, known_at=rng.known_at,
                coverage_ok=rng.coverage_ok, evidence_ids=rng.member_ids)
        if rid == "O046":
            if config.get("clock_variant") == "nyam" and _clock(rng) != ((9, 0), (10, 0)):
                raise GeometryError("NYAM box must be 09:00-10:00 ET")
            qualifier = _optional_audited_source_values(config, ("source_clock_verified",))
            verified = qualifier.get("source_clock_verified")
            holes = list(range_holes)
            if not verified: holes.append("HOLE:O046:source_clock")
            return _r(rid, {"box_high": rng.H, "box_low": rng.L,
                "box_width": rng.W, "box_id": rng.range_id,
                "formation_start": rng.formation_start, "formation_end": rng.formation_end,
                "known_at": rng.known_at, "boundary_ids": {
                    "high": f"{rng.range_id}:high", "low": f"{rng.range_id}:low"},
                "source_clock_verified": verified, "coverage_ok": rng.coverage_ok}, holes=holes,
                known_at=rng.known_at, coverage_ok=rng.coverage_ok, evidence_ids=rng.member_ids)
        if rid == "O048":
            required = ("period_id", "period_kind", "period_scope", "period_end")
            holes = list(range_holes) + [f"HOLE:O048:{key}" for key in required if config.get(key) is None]
            qualifier = _optional_audited_source_values(config, ("active_state", "retirement_policy"))
            holes += [f"HOLE:O048:{key}" for key in ("active_state", "retirement_policy")
                      if qualifier.get(key) is None]
            return _r(rid, {"prior_high": rng.H, "prior_low": rng.L,
                "period_id": config.get("period_id"), "period_kind": config.get("period_kind"),
                "period_scope": config.get("period_scope"), "period_end": config.get("period_end"),
                "known_at": rng.known_at, "active_state": qualifier.get("active_state"),
                "retirement_policy": qualifier.get("retirement_policy")}, holes=holes,
                known_at=rng.known_at, coverage_ok=rng.coverage_ok, evidence_ids=rng.member_ids)
        raise GeometryError("unknown native range alias")
    except GeometryError as exc:
        return _invalid(rid, str(exc), "complete_membership")


def native_o020(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return _native_range_alias("O020", config, resolved, clock=((9, 30), (16, 0)))


def native_o025(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return _native_range_alias("O025", config, resolved)


def native_o046(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return _native_range_alias("O046", config, resolved)


def native_o048(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return _native_range_alias("O048", config, resolved)


def native_o049(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        qualifier = _audited_source_values(config, ("source_clock_verified", "tdo_required",
            "role", "close_through_mode", "side"))
        if qualifier.get("source_clock_verified") is not True:
            raise GeometryError("true-day-open clock is not verified")
        start = ns_to_et(resolved.start_ns)
        if (start.hour, start.minute) != (0, 0):
            raise GeometryError("TDO must start at 00:00 ET")
        rows = [row for row in resolved.rows() if row.get("action") == "T"
                and row.get("event_ns") is not None
                and resolved.start_ns <= row["event_ns"] < resolved.end_ns]
        if not rows or resolved.coverage_ok is not True:
            raise GeometryError("opening execution/coverage is unavailable")
        first, opening_known, ambiguous = _opening_execution(rows)
        tdo_id = config.get("tdo_id") or f"TDO:{resolved.instrument_id}:{start.date()}"
        if first is None:
            return _r("O049", {"tdo_id": tdo_id, "tdo_price": None,
                "tdo_known_at": opening_known, "role": qualifier.get("role"),
                "close_through_tdo": None, "close_through_mode": qualifier.get("close_through_mode"),
                "opening_event_id": None, "source_tdo_close_confirmed": None,
                "close_completed": None, "distinct": None},
                holes=["HOLE:O049:opening_event_order"], known_at=opening_known,
                coverage_ok=None, evidence_ids=[str(row["event_id"]) for row in ambiguous])
        bar = _confirmation_bar(config, resolved)
        if bar is not None and bar["end"]-bar["start"] != 5*MINUTE_NS:
            raise GeometryError("TDO confirmation must be an actual complete five-minute bar")
        confirmation_known = None if bar is None else bar.get("known_at", bar["end"])
        result_known = max(value for value in (opening_known, confirmation_known) if value is not None)
        result = o049({"tdo": first["price"], "tdo_id": tdo_id,
            "tdo_known_at": opening_known, "known_at": result_known,
            "opening_event_id": first["event_id"], "tdo_required": qualifier.get("tdo_required"),
            "role": qualifier.get("role"), "close_through_mode": qualifier.get("close_through_mode"),
            "side": qualifier.get("side"), "confirmation_close": None if bar is None else bar["C"],
            "complete_clock_five_minute_bar": None if bar is None else True})
        result.evidence_ids = [str(first["event_id"]), *([] if bar is None else [str(bar["candle_id"])])]
        return result
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O049", str(exc), "opening_event")


def native_o050(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        qualifier = _audited_source_values(config, ("source_reclaim_criterion",))
        criterion = qualifier.get("source_reclaim_criterion")
        if criterion not in {"strict", "strict_cross_below_then_above"}:
            raise GeometryError("unsupported source reclaim criterion")
        open_at = resolved.start_ns
        local = ns_to_et(open_at)
        if (local.hour, local.minute) != (9, 30):
            raise GeometryError("cash open must be 09:30 ET")
        rows = [row for row in resolved.rows() if row.get("action") == "T"
                and row.get("event_ns") is not None and row["event_ns"] >= open_at]
        if not rows or resolved.coverage_ok is not True:
            raise GeometryError("cash-open execution/coverage is unavailable")
        first, opening_known, ambiguous = _opening_execution(rows)
        as_of = resolved.end_ns
        if first is None:
            return _r("O050", {"cash_open": None, "open_event_id": None,
                "known_at": opening_known, "cross_below_at": None,
                "cross_above_at": None, "source_open_reclaim": None,
                "reclaim_at": None, "as_of": as_of},
                holes=["HOLE:O050:opening_event_order"], known_at=opening_known,
                coverage_ok=None, evidence_ids=[str(row["event_id"]) for row in ambiguous])
        open_price = first["price"]
        eligible = sorted((row for row in rows if row["event_ns"] < as_of),
                          key=_native_event_key)
        below = next((row for row in eligible if row["price"] < open_price), None)
        above = next((row for row in eligible if row["price"] > open_price), None)
        reclaim = None
        if below:
            reclaim = next((row for row in eligible if row["event_ns"] > below["event_ns"] and row["price"] > open_price), None)
        known = max([opening_known, *(row["known_at"] for row in eligible)])
        return _r("O050", {"cash_open": open_price, "open_event_id": first["event_id"],
            "known_at": known, "cross_below_at": None if below is None else below["event_ns"],
            "cross_above_at": None if above is None else above["event_ns"],
            "source_open_reclaim": reclaim is not None,
            "reclaim_at": None if reclaim is None else reclaim["event_ns"],
            "as_of": as_of}, holes=[],
            known_at=known, evidence_ids=[row["event_id"] for row in eligible])
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O050", str(exc), "opening_event")


def native_o027(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        if resolved.coverage_ok is not True:
            raise GeometryError("current RVOL interval is incomplete")
        rows = resolved.rows()
        volumes = []
        for row in rows:
            if row.get("action") == "T": volumes.append(_d(row.get("size"), "trade size"))
            elif row.get("start") is not None:
                if row.get("complete") is not True: raise GeometryError("incomplete volume bar")
                volumes.append(_d(row.get("V", row.get("volume")), "bar volume"))
        current = sum(volumes, Decimal(0))
        baseline_members = config.get("baseline_members")
        if not isinstance(baseline_members, list) or not baseline_members:
            return _r("O027", {"current_volume": current, "baseline_volume": None,
                "rvol": None, "source_high_rvol": None, "sample_ids": [],
                "baseline_statistic": config.get("baseline_statistic"),
                "known_at": max(resolved.end_ns, resolved.known_at)},
                holes=["HOLE:O027:baseline"], known_at=max(resolved.end_ns, resolved.known_at), coverage_ok=None)
        if config.get("baseline_statistic") != "arithmetic_mean":
            raise GeometryError("only an explicitly selected arithmetic mean baseline is implemented")
        if any(member.get("same_clock") is not True or member.get("coverage_ok") is not True for member in baseline_members):
            raise GeometryError("RVOL baseline members are not complete same-clock intervals")
        base_values = [_d(member.get("volume"), "baseline volume") for member in baseline_members]
        baseline = sum(base_values, Decimal(0)) / len(base_values)
        if baseline <= 0: raise GeometryError("RVOL baseline must be positive")
        threshold = dec(config.get("high_threshold")); rvol = current / baseline
        known = max(resolved.end_ns, resolved.known_at, *(member["known_at"] for member in baseline_members))
        return _r("O027", {"current_volume": current, "baseline_volume": baseline,
            "rvol": rvol, "source_high_rvol": None if threshold is None else rvol >= threshold,
            "sample_ids": [member["sample_id"] for member in baseline_members],
            "baseline_statistic": "arithmetic_mean", "known_at": known},
            holes=[] if threshold is not None else ["HOLE:O027:classification"], known_at=known)
    except GeometryError as exc:
        return _invalid("O027", str(exc), "volume_members")


def o002(inp: dict) -> RecipeResult:
    try:
        lo, hi = _d(inp.get("lo"), "lo"), _d(inp.get("hi"), "hi")
        if lo > hi: raise GeometryError("band bounds are reversed")
        width = dec(inp.get("W"))
        if width is not None and width <= 0: raise GeometryError("parent width must be positive")
        q = dec(inp.get("tick_size", inp.get("q"))); tolerance = dec(inp.get("tolerance_ticks"))
        if tolerance is not None and (q is None or q <= 0): raise GeometryError("tolerance requires definition tick size")
        pad = Decimal(0) if tolerance is None else tolerance*q
        events = sorted(inp.get("events", ()), key=lambda row: (row.get("event_ns", row.get("t", 0)), row.get("sequence", 0)))
        bars = inp.get("bars", ())
        contact = next((row for row in events if lo-pad <= _d(row.get("price"), "event price") <= hi+pad), None)
        prices = [_d(row.get("price"), "event price") for row in events]
        strict = None
        if prices:
            upper = any(price > hi for price in prices); lower = any(price < lo for price in prices)
            strict = "both" if upper and lower else "upper" if upper else "lower" if lower else "none"
        overlap = None if not events or inp.get("coverage_ok") is not True else contact is not None
        close_return = None
        sweep_depth = None
        if bars:
            if any(row.get("complete") is not True or row.get("H") is None or row.get("L") is None for row in bars):
                return _r("O002", {"contact_at": None if contact is None else contact.get("event_ns", contact.get("t")),
                    "price_overlap": None, "strict_break_side": strict, "sweep_depth": None,
                    "sweep_depth_ticks": None, "literal_close_return": None,
                    "source_reject": None, "source_hold": None, "tolerance_ticks": tolerance},
                    holes=["HOLE:O002:complete_bar"], known_at=inp.get("known_at"), coverage_ok=None)
            bar_contact = next((row for row in bars
                if _d(row["H"], "H") >= lo-pad and _d(row["L"], "L") <= hi+pad), None)
            overlap = bar_contact is not None
            if contact is None and bar_contact is not None:
                contact = {"event_ns": bar_contact.get("known_at", bar_contact.get("end"))}
            bar_upper = any(_d(row["H"], "H") > hi for row in bars)
            bar_lower = any(_d(row["L"], "L") < lo for row in bars)
            strict = ("both" if bar_upper and bar_lower else "upper" if bar_upper
                      else "lower" if bar_lower else "none")
            side = inp.get("side")
            last = bars[-1]; close = _d(last.get("C"), "close")
            close_return = lo < close < hi
            if side == "upper": sweep_depth = max(Decimal(0), max(_d(row["H"], "H") for row in bars)-hi)
            elif side == "lower": sweep_depth = max(Decimal(0), lo-min(_d(row["L"], "L") for row in bars))
        criterion = inp.get("source_criterion")
        source_reject = None if criterion is None else inp.get("source_reject_evidence") is True
        source_hold = None if criterion is None else inp.get("source_hold_evidence") is True
        holes = [] if criterion is not None else ["HOLE:O002:source_confirmation"]
        return _r("O002", {"contact_at": None if contact is None else contact.get("event_ns", contact.get("t")),
            "price_overlap": overlap, "strict_break_side": strict, "sweep_depth": sweep_depth,
            "sweep_depth_ticks": None if sweep_depth is None or q is None else sweep_depth/q,
            "literal_close_return": close_return, "source_reject": source_reject,
            "source_hold": source_hold, "tolerance_ticks": tolerance,
            "observed_high": max((_d(row["H"],"H") for row in bars),default=max(prices,default=None)),
            "observed_low": min((_d(row["L"],"L") for row in bars),default=min(prices,default=None)),
            "reference_band": [lo,hi], "reference_lineage_id": inp.get("reference_lineage_id")}, holes=holes,
            known_at=inp.get("known_at"), coverage_ok=inp.get("coverage_ok"))
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O002", str(exc))


def o005(inp: dict) -> RecipeResult:
    rng = inp.get("range")
    if isinstance(rng, RangeGeometry): return _r("O005", _range_payload(rng), known_at=rng.known_at, evidence_ids=rng.member_ids)
    return _r("O005", {"range_id": inp.get("range_id"), "L": dec(inp.get("L")), "H": dec(inp.get("H")),
        "W": None, "formation_start": inp.get("start_ns"), "formation_end": inp.get("end_ns"),
        "range_known_at": None, "range_frozen": False}, holes=["HOLE:O005:native_members"], base_ok=None, coverage_ok=None)


def o006(inp: dict) -> RecipeResult:
    return o005(inp) if not isinstance(inp.get("range"), RangeGeometry) else _r("O006", {**_range_payload(inp["range"]), "source_clock_verified": inp.get("source_clock_verified")}, holes=[] if inp.get("source_clock_verified") is True else ["HOLE:O006:source_clock"], known_at=inp["range"].known_at)


def _selected_contact(inp: Mapping[str, Any], bands: Sequence[Sequence[Decimal]]) -> dict:
    """Compare a separately observed contact against this exact parent geometry."""
    contact = inp.get("contact_observation")
    empty = {"selected_contact": None, "selected_contact_at": None}
    if contact is None: return empty
    if not isinstance(contact, Mapping): raise GeometryError("contact observation must be identified")
    parent_id = inp.get("parent_id", inp.get("range_id", inp.get("impulse_id")))
    if not parent_id or contact.get("reference_lineage_id") != parent_id:
        raise GeometryError("contact belongs to another reference lineage")
    band = contact.get("reference_band")
    if not isinstance(band, (list, tuple)) or len(band) != 2:
        raise GeometryError("contact lacks exact reference band")
    selected = [dec(band[0]), dec(band[1])]
    if selected not in [list(b) for b in bands]:
        raise GeometryError("contact band differs from selected source geometry")
    at = contact.get("contact_at")
    known = contact.get("known_at")
    if at is not None and (type(at) is not int or type(known) is not int or at > known):
        raise GeometryError("contact backdates its observation")
    if at is not None and (type(inp.get("known_at")) is not int or inp["known_at"]>at):
        raise GeometryError("contact precedes its selected geometry availability")
    return {"selected_contact": contact.get("price_overlap"), "selected_contact_at": at, "_selected_contact_known_at": known}


def o007(inp: dict) -> RecipeResult:
    try:
        low, high = _d(inp.get("L"), "L"), _d(inp.get("H"), "H")
        width = high-low
        if width <= 0: raise GeometryError("range width must be positive")
        supplied = dec(inp.get("W"))
        if supplied is not None and supplied != width: raise GeometryError("supplied width does not match parent bounds")
        return _r("O007", {"parent_id": inp.get("range_id", inp.get("parent_id")),
            "q25": low+Decimal(".25")*width, "eq": low+Decimal(".5")*width,
            "q75": low+Decimal(".75")*width, **_selected_contact(inp, [[low+f*width]*2 for f in (Decimal(".25"),Decimal(".5"),Decimal(".75"))])}, holes=[] if inp.get("range_id", inp.get("parent_id")) else ["HOLE:O007:parent_id"], known_at=inp.get("known_at"))
    except GeometryError as exc: return _invalid("O007", str(exc), "parent")


def o008(inp: dict) -> RecipeResult:
    open_ref, close_ref = dec(inp.get("range_open_ref")), dec(inp.get("range_close_ref"))
    anchor = inp.get("anchor_id"); verified = inp.get("reference_verified") is True and anchor is not None
    source_event, target_event = inp.get("source_event"), inp.get("target_event")
    directed = None
    if source_event is not None and target_event is not None:
        directed = source_event.get("reference_id") == inp.get("path_source_id") and target_event.get("reference_id") == inp.get("path_target_id") and source_event.get("known_at") < target_event.get("known_at")
    holes = []
    if not verified: holes.append("HOLE:O008:source_open_identity")
    if inp.get("directed_path_required") and directed is None: holes.append("HOLE:O008:directed_path")
    return _r("O008", {"range_open_ref": open_ref, "range_close_ref": close_ref,
        "anchor_id": anchor, "reference_verified": True if verified else None,
        "directed_path": directed, "literal_source_label": inp.get("literal_source_label")},
        holes=holes, known_at=inp.get("known_at"), coverage_ok=None if holes else True)


def o009(inp: dict) -> RecipeResult:
    try:
        width = _d(inp.get("W"), "W")
        if width <= 0: raise GeometryError("range width must be positive")
        tick = dec(inp.get("tick_size", inp.get("q"))); price = dec(inp.get("price_denominator", inp.get("P"))); prior = dec(inp.get("prior_range_width"))
        if tick is not None and tick <= 0: raise GeometryError("tick size must be positive")
        if price is not None and price <= 0: raise GeometryError("price denominator must be positive")
        if prior is not None and prior <= 0: raise GeometryError("prior width must be positive")
        holes=[]
        if inp.get("source_width_class") is None: holes.append("HOLE:O009:source_class")
        return _r("O009", {"width_points": width,
            "width_ticks": None if tick is None else width/tick,
            "price_percent": None if price is None else Decimal(100)*width/price,
            "width_ratio": None if prior is None else width/prior,
            "source_width_class": inp.get("source_width_class"),
            "denominator_ids": list(inp.get("denominator_ids", ()))}, holes=holes,
            known_at=max((v for v in inp.get("dependency_known_ats", [inp.get("known_at")]) if v is not None), default=None))
    except GeometryError as exc: return _invalid("O009", str(exc), "denominator")


def o010(inp: dict) -> RecipeResult:
    try:
        high, low = _d(inp.get("H"), "H"), _d(inp.get("L"), "L")
        if high <= low: raise GeometryError("range bounds require H>L")
        start, end, as_of = inp.get("window_start"), inp.get("window_end"), inp.get("as_of", inp.get("window_end"))
        events = [row for row in inp.get("events", ()) if (start is None or row["t"] >= start) and (as_of is None or row["t"] < as_of)]
        high_events = [row for row in events if dec(row["price"]) > high]; low_events=[row for row in events if dec(row["price"]) < low]
        h = min(high_events, key=lambda row: row["t"]) if high_events else None; l=min(low_events,key=lambda row:row["t"]) if low_events else None
        coverage = inp.get("coverage_ok") is True and end is not None and as_of is not None and as_of >= end
        if h and l: path="both"
        elif coverage: path="high_only" if h else "low_only" if l else "neither"
        else: path="high_so_far" if h else "low_so_far" if l else "unknown"
        first = None if not h and not l else "high" if h and (not l or h["t"] < l["t"]) else "low" if l and (not h or l["t"] < h["t"]) else None
        first_at = min((v["t"] for v in (h,l) if v), default=None)
        eq=(high+low)/2; eq_return=next((row["t"] for row in events if row["t"]>first_at and dec(row["price"])==eq),None) if h or l else None
        holes=[] if coverage or h or l else ["HOLE:O010:coverage"]
        if h and l and h["t"]==l["t"]: holes.append("HOLE:O010:ordering")
        return _r("O010", {"high_break_at":None if h is None else h["t"],"low_break_at":None if l is None else l["t"],
            "path":path,"first_side":first,"eq_return_at":eq_return,"window_complete":coverage},holes=holes,
            known_at=end if coverage else max((row["t"] for row in events),default=inp.get("known_at")),coverage_ok=True if coverage else None)
    except (GeometryError, KeyError) as exc:return _invalid("O010",str(exc))


def o011(inp: dict) -> RecipeResult:
    rng = inp.get("range")
    if isinstance(rng, RangeGeometry):
        return _r("O011", {"on_high": rng.H, "on_low": rng.L,
            "on_width": rng.W, "window_id": inp.get("window_id", rng.range_id),
            "known_at": rng.known_at, "formation_start": rng.formation_start,
            "formation_end": rng.formation_end, "instrument_id": rng.instrument_id,
            "coverage_ok": rng.coverage_ok, "member_ids": list(rng.member_ids)},
            holes=[] if rng.coverage_ok is True else ["HOLE:O011:coverage"],
            known_at=rng.known_at, coverage_ok=rng.coverage_ok,
            evidence_ids=rng.member_ids)
    return _r("O011", {"on_high":dec(inp.get("H")),"on_low":dec(inp.get("L")),"on_width":None,
        "window_id":inp.get("window_id"),"known_at":inp.get("known_at"),"formation_start":inp.get("start_ns"),
        "formation_end":inp.get("end_ns"),"instrument_id":inp.get("instrument_id"),"coverage_ok":None,"member_ids":[]},
        holes=["HOLE:O011:native_members"],base_ok=None,coverage_ok=None)


def o012(inp: dict) -> RecipeResult:
    try:
        price=_d(inp.get("reference_px"),"reference price"); known=inp.get("reference_known_at"); decision=inp.get("decision_at")
        side=inp.get("side"); criterion=inp.get("sweep_definition")
        events=sorted(inp.get("events",()),key=lambda row:row["t"])
        qualifying=[]
        if criterion is not None:
            qualifying=[row for row in events if row["t"]>=known and ((side=="high" and dec(row["price"])>price) or (side=="low" and dec(row["price"])<price)) and row.get("qualifies",True)]
        first=qualifying[0] if qualifying else None; scope=inp.get("consumption_scope")
        purged_at=None if first is None else first["t"]
        before=None if decision is None or known is None else (purged_at is not None and purged_at < decision)
        rth_exception=scope=="rth_only" and first is not None and first.get("session")!="rth"
        active=True if rth_exception else (None if criterion is None else not (purged_at is not None and (decision is None or purged_at < decision)))
        holes=[] if criterion is not None and scope else [f"HOLE:O012:{'sweep_definition' if criterion is None else 'consumption_scope'}"]
        return _r("O012",{"reference_id":inp.get("reference_id"),"active_before_use":active,"purged_at":purged_at,
            "consumption_scope":scope,"purge_known_at":None if first is None else first.get("known_at",first["t"]),
            "source_purged_context":before,"rth_exception_applied":rth_exception},holes=holes,
            known_at=None if first is None else first.get("known_at",first["t"]),coverage_ok=inp.get("coverage_ok"))
    except (GeometryError,KeyError,TypeError) as exc:return _invalid("O012",str(exc))


def o013(inp: dict) -> RecipeResult:
    try:
        price=_d(inp.get("open_px"),"open price")
        value=inp.get("prior_value"); prior=inp.get("prior_range"); current=inp.get("current_range")
        rel_value=_relation(price,dec(value[0]),dec(value[1])) if value else None
        rel_prior=_relation(price,dec(prior[0]),dec(prior[1])) if prior else None
        rel_current=_relation(price,dec(current[0]),dec(current[1])) if current else None
        use=inp.get("use_at"); rvol_at=inp.get("rvol_known_at"); context=inp.get("opening_context")
        holes=[]
        for name,value_ in (("prior_value",value),("prior_range",prior)):
            if value_ is None:holes.append(f"HOLE:O013:{name}")
        if rvol_at is not None and use is not None and rvol_at>use: context=None;holes.append("HOLE:O013:rvol_ordering")
        return _r("O013",{"open_vs_value":rel_value,"open_vs_range":rel_prior,"open_vs_current_range":rel_current,
            "opening_context":context,"rvol_known_at":rvol_at,"open_at":inp.get("open_at"),
            "reference_ids":list(inp.get("reference_ids",()))},holes=holes,known_at=max((v for v in [inp.get("open_known_at"),*(inp.get("reference_known_ats",()))] if v is not None),default=None),coverage_ok=None if holes else True)
    except (GeometryError,IndexError) as exc:return _invalid("O013",str(exc))


def o014(inp: dict) -> RecipeResult:
    try:
        low,high=_d(inp.get("L"),"L"),_d(inp.get("H"),"H");width=high-low
        if width<=0:raise GeometryError("range width must be positive")
        supplied=dec(inp.get("W"))
        if supplied is not None and supplied!=width:raise GeometryError("parent width mismatch")
        ks=tuple(dec(v) for v in inp.get("k_values",("0.1","0.2","0.3","0.5")))
        ladder={str(k):{"upper":high+k*width,"lower":low-k*width} for k in ks}
        side=inp.get("side");events=sorted(inp.get("events",()),key=lambda row:row["t"])
        sweep=next((row for row in events if (side=="upper" and dec(row["price"])>high) or (side=="lower" and dec(row["price"])<low)),None)
        depth=None if sweep is None else max(Decimal(0),dec(sweep["price"])-high if side=="upper" else low-dec(sweep["price"]))
        holes=[] if inp.get("coordinate_convention_verified") is True and inp.get("selected_band") is not None else ["HOLE:O014:source_band"]
        return _r("O014",{"upper_ladder":{k:v["upper"] for k,v in ladder.items()},"lower_ladder":{k:v["lower"] for k,v in ladder.items()},
            "selected_band":inp.get("selected_band"),"sweep_depth_points":depth,"sweep_depth_W":None if depth is None else depth/width,
            "touch_at":None if sweep is None else sweep["t"],"parent_id":inp.get("range_id")},holes=holes,known_at=inp.get("known_at"))
    except (GeometryError,KeyError) as exc:return _invalid("O014",str(exc),"parent")


def o015(inp: dict) -> RecipeResult:
    try:
        low,high=_d(inp.get("L"),"L"),_d(inp.get("H"),"H");width=high-low
        if width<=0:raise GeometryError("range width must be positive")
        if dec(inp.get("W",width))!=width:raise GeometryError("projection width does not match selected parent")
        if inp.get("coordinate_convention_verified") is not True: return _r("O015",{"upper_band":None,"lower_band":None,"parent_id":inp.get("parent_id"),"known_at":inp.get("known_at")},holes=["HOLE:O015:coordinate_convention"],known_at=inp.get("known_at"),coverage_ok=None)
        return _r("O015",{"upper_band":[high+Decimal("1.33")*width,high+Decimal("1.66")*width],
            "lower_band":[low-Decimal("1.66")*width,low-Decimal("1.33")*width],"parent_id":inp.get("parent_id"),"known_at":inp.get("known_at"), **_selected_contact(inp, [[high+Decimal("1.33")*width,high+Decimal("1.66")*width],[low-Decimal("1.66")*width,low-Decimal("1.33")*width]])},holes=[] if inp.get("parent_id") else ["HOLE:O015:parent_id"],known_at=inp.get("known_at"))
    except GeometryError as exc:return _invalid("O015",str(exc),"parent")


def o016(inp: dict) -> RecipeResult:
    try:
        outer_id,inner_id=inp.get("outer_id"),inp.get("inner_id")
        outer_l,outer_h=_d(inp.get("outer_L"),"outer_L"),_d(inp.get("outer_H"),"outer_H")
        inner_l,inner_h=dec(inp.get("inner_L")),dec(inp.get("inner_H"))
        if outer_h<=outer_l:raise GeometryError("outer width must be positive")
        if (inner_l is None)!=(inner_h is None):raise GeometryError("inner bounds must be supplied together")
        if inner_l is not None and inner_h<=inner_l:raise GeometryError("inner width must be positive")
        parent=inp.get("projection_parent_id");binding=parent if parent in {outer_id,inner_id} else None
        if parent is not None and binding is None:raise GeometryError("projection parent is not an identified span")
        holes=[]
        if inner_l is None:holes.append("HOLE:O016:inner_bounds")
        if inp.get("source_label") is None:holes.append("HOLE:O016:source_label")
        holes.append("HOLE:O016:inner_range_construction")
        return _r("O016",{"outer_id":outer_id,"inner_id":inner_id,"outer_width":outer_h-outer_l,
            "inner_width":None if inner_l is None else inner_h-inner_l,"outer_mid":(outer_h+outer_l)/2,
            "inner_mid":None if inner_l is None else (inner_h+inner_l)/2,"parent_binding":binding,
            "inner_geometry_known":None if inner_l is None else True,"automatic_inner_span":None,
            "literal_labels":list(inp.get("literal_labels",()))},holes=holes,known_at=inp.get("known_at"),coverage_ok=None)
    except GeometryError as exc:return _invalid("O016",str(exc))


def o017(inp: dict) -> RecipeResult:
    try:
        def band(name):
            raw=inp.get(name)
            if raw is None:return None
            lo,hi=dec(raw[0]),dec(raw[1])
            if lo>hi:raise GeometryError(f"{name} endpoints are reversed")
            return [lo,hi]
        average,median,minimum=band("average"),band("median"),band("min_average")
        settings=inp.get("settings");known=inp.get("snapshot_known_at",inp.get("known_at"));use=inp.get("use_at")
        if known is not None and use is not None and known>use:return _invalid("O017","SessionStat snapshot is available after use","ordering")
        midpoint_parent=inp.get("midpoint_parent")
        midpoint=None
        if midpoint_parent in {"average","median","min_average"}:
            selected={"average":average,"median":median,"min_average":minimum}[midpoint_parent]
            midpoint=None if selected is None else sum(selected,Decimal(0))/2
        holes=[]
        if average is None:holes.append("HOLE:O017:average")
        if minimum is None:holes.append("HOLE:O017:min_average")
        if not isinstance(settings,Mapping) or any(settings.get(k) is None for k in ("source_version","platform","chart_timeframe","session","reset","lookback")):holes.append("HOLE:O017:settings")
        return _r("O017",{"average_lo":None if average is None else average[0],"average_hi":None if average is None else average[1],
            "median_lo":None if median is None else median[0],"median_hi":None if median is None else median[1],
            "min_average_lo":None if minimum is None else minimum[0],"min_average_hi":None if minimum is None else minimum[1],
            "midpoint_when_labeled":midpoint,"midpoint_parent":midpoint_parent,
            "source_band_known":True if not holes else None,"automatic_bands":None,"settings":settings},holes=holes,known_at=known,coverage_ok=None if holes else True)
    except (GeometryError,IndexError) as exc:return _invalid("O017",str(exc))


def o018(inp: dict) -> RecipeResult:
    low,high,mid=dec(inp.get("ev_low")),dec(inp.get("ev_high")),dec(inp.get("ev_mid",inp.get("midpoint")))
    known=inp.get("snapshot_known_at",inp.get("known_at"));use=inp.get("use_at")
    if low is not None and high is not None and low>high:return _invalid("O018","EVRange bounds are reversed")
    if known is not None and use is not None and known>use:return _invalid("O018","EVRange snapshot is available after use use","ordering")
    required=inp.get("source_version") and inp.get("anchor_id") and known is not None and (mid is not None or low is not None and high is not None)
    holes=[] if required else ["HOLE:O018:source_snapshot"]
    return _r("O018",{"ev_low":low,"ev_high":high,"ev_mid_if_supplied":mid,
        "ev_reference_known":True if required else None,"automatic_ev":None,
        "ev_id":inp.get("ev_id"),"anchor_id":inp.get("anchor_id"),"source_version":inp.get("source_version")},holes=holes,known_at=known,coverage_ok=None if holes else True)


def o019(inp: dict) -> RecipeResult:
    try:
        lo,hi=_d(inp.get("lo"),"lo"),_d(inp.get("hi"),"hi")
        if lo>hi:raise GeometryError("P-zone bounds are reversed")
        known=inp.get("snapshot_known_at");touch=inp.get("touch_at");use=inp.get("use_at")
        source_known=None if known is None or touch is None else known<=touch
        history=sorted(inp.get("state_events",()),key=lambda row:row["known_at"])
        state=None
        for event in history:
            if use is None or event["known_at"]<=use:state=event.get("active")
        source_id,target_id=inp.get("path_source_id"),inp.get("path_target_id")
        path_events=inp.get("path_events",())
        directed=None
        if len(path_events)>=2:
            directed=path_events[0].get("reference_id")==source_id and path_events[-1].get("reference_id")==target_id and path_events[0]["known_at"]<path_events[-1]["known_at"]
        holes=[]
        if known is None:holes.append("HOLE:O019:known_at")
        if not history:holes.append("HOLE:O019:active_policy")
        if inp.get("settings") is None:holes.append("HOLE:O019:settings")
        return _r("O019",{"pzone_id":inp.get("pzone_id"),"lo":lo,"hi":hi,"anchor_at":inp.get("anchor_at"),
            "source_zone_known":source_known,"active_at_use":state,"directed_path_recorded":directed,
            "source_id":source_id,"target_id":target_id,"settings":inp.get("settings")},holes=holes,known_at=known,coverage_ok=None if holes else True)
    except (GeometryError,KeyError) as exc:return _invalid("O019",str(exc))


def o020(inp: dict) -> RecipeResult:
    return _r("O020",{"prior_rth_high":dec(inp.get("prior_rth_h")),"prior_rth_low":dec(inp.get("prior_rth_l")),
        "prior_range_id":inp.get("prior_range_id"),"known_at":inp.get("known_at"),"rth_active_objectives":[],
        "chosen_draw":None,"current_direction":None,"coverage_ok":None},holes=["HOLE:O020:native_members"],base_ok=None,coverage_ok=None)


def o021(inp: dict) -> RecipeResult:
    event=inp.get("event_ns",inp.get("actual_action_at"));start,end=inp.get("window_start"),inp.get("window_end")
    purpose=inp.get("purpose");branch=inp.get("branch")
    if event is None:return _invalid("O021","actual action event is missing","event")
    at_open=(ns_to_et(event).hour,ns_to_et(event).minute)==(9,30)
    membership=None;ambiguity=False
    if start is not None and end is not None:
        if event in {start,end} and inp.get("boundary_convention") is None:ambiguity=True
        else:membership=start<=event<end if inp.get("boundary_convention","left_closed_right_open")=="left_closed_right_open" else start<event<end
    holes=[]
    if start is None or end is None:holes.append("HOLE:O021:source_window")
    if purpose is None or branch is None:holes.append("HOLE:O021:purpose")
    if ambiguity:holes.append("HOLE:O021:boundary_convention");membership=None
    return _r("O021",{"at_rth_open":at_open,"source_time_window":membership,"exit_window_recorded":purpose=="exit" and start is not None,
        "actual_action_at":event,"purpose":purpose,"branch":branch,"boundary_ambiguous":ambiguity},holes=holes,known_at=event,coverage_ok=None if holes else True)


def o022(inp: dict) -> RecipeResult:
    label=inp.get("label");recorded=inp.get("recorded_at");use=inp.get("use_at")
    if recorded is not None and use is not None and recorded>use:return _invalid("O022","cleanliness label recorded after use","ordering")
    valid=label in {"clean","unclean","mixed","preferred","not_preferred"}
    holes=[] if valid and inp.get("session_id") else ["HOLE:O022:source_record"]
    return _r("O022",{"source_cleanliness_label":label if valid else None,
        "session_selected_before_use":None if recorded is None or use is None else recorded<=use,
        "automatic_cleanliness":None,"session_id":inp.get("session_id"),"reason":inp.get("reason")},holes=holes,known_at=recorded,coverage_ok=None if holes else True)


def o023(inp: dict) -> RecipeResult:
    label=inp.get("phase_label",inp.get("phase"));known=inp.get("known_at");use=inp.get("use_at")
    if known is not None and use is not None and known>use:return _invalid("O023","phase annotation is retrospective at use","ordering")
    transitions=inp.get("transition_events",())
    sequence=_ordered(*(event.get("known_at") for event in transitions)) if transitions else None
    holes=["HOLE:O023:automatic_phase"]
    if label is None:holes.append("HOLE:O023:phase_label")
    return _r("O023",{"phase_label":label,"phase_known_at":known,"used_as_context":inp.get("used_as_context") is True,
        "transition_sequence":sequence,"automatic_phase":None,"contemporaneous":inp.get("contemporaneous")},holes=holes,known_at=known,coverage_ok=None)


def o024(inp: dict) -> RecipeResult:
    attempts=inp.get("attempts",());at=inp.get("evaluation_at",inp.get("use_at"));level=inp.get("level_id");branch=inp.get("branch")
    distinct={}
    for attempt in attempts:
        aid=attempt.get("attempt_id",attempt.get("id"))
        if aid is None:continue
        if level is not None and attempt.get("level_id",level)!=level:continue
        if branch is not None and attempt.get("branch",branch)!=branch:continue
        ended=attempt.get("failure_known_at",attempt.get("ended_at",attempt.get("t")))
        if at is not None and ended is not None and ended>at:continue
        if attempt.get("outcome") in {"failed","failure"} or attempt.get("failed") is True:distinct[aid]=ended
    count=len(distinct);three=count>=3
    continued=inp.get("continuing_through")
    invalidated=True if three or continued is True or inp.get("rejection_absent") is True else False if inp.get("invalidation_evidence_complete") is True else None
    prior,new=dec(inp.get("prior_allocation")),dec(inp.get("new_allocation"))
    alloc=None if prior is None or new is None else new<=Decimal(".5")*prior
    holes=[]
    if invalidated is None:holes.append("HOLE:O024:invalidation_evidence")
    if inp.get("continued_after_failure") and alloc is None:holes.append("HOLE:O024:allocation")
    return _r("O024",{"failed_attempt_count":count,"failed_attempt_ids":sorted(distinct),"three_failed_attempts":three,
        "reversal_invalidated":invalidated,"later_allocation_ok":alloc},holes=holes,known_at=max((v for v in distinct.values() if v is not None),default=inp.get("known_at")),coverage_ok=None if holes else True)


def o025(inp: dict) -> RecipeResult:
    high,low=dec(inp.get("or_h")),dec(inp.get("or_l"));mid=None if high is None or low is None else (high+low)/2
    known=inp.get("end_ns");verified=inp.get("source_clock_verified") is True and inp.get("or_id") is not None and known is not None
    touch=next((event for event in inp.get("events",()) if known is not None and event["t"]>known and dec(event["price"])==mid),None) if mid is not None else None
    return _r("O025",{"or_mid":mid,"or_high":high,"or_low":low,"or_id":inp.get("or_id"),"or_known":True if verified else None,
        "subsequent_mid_retrace":None if touch is None else touch["t"],"known_at":known},holes=[] if verified else ["HOLE:O025:or_clock"],known_at=known,coverage_ok=None if not verified else True)


def o026(inp: dict) -> RecipeResult:
    try:
        low,high=_d(inp.get("low"),"low"),_d(inp.get("high"),"high")
        if high<=low:raise GeometryError("swing width must be positive")
        if inp.get("low_id") and inp.get("high_id") and inp.get("swing_id") is None:raise GeometryError("swing endpoint parent identity is missing")
        known=max(inp["low_confirmed_at"],inp["high_confirmed_at"])
        mid=(high+low)/2;contact=next((row for row in inp.get("events",()) if row["t"]>known and dec(row["price"])==mid),None)
        holes=[] if inp.get("timeframe") and inp.get("swing_id") else ["HOLE:O026:source_selection"]
        return _r("O026",{"swing_mid":mid,"swing_known_at":known,"later_mid_contact":None if contact is None else contact["t"],
            "swing_id":inp.get("swing_id"),"endpoint_ids":[inp.get("low_id"),inp.get("high_id")],"automatic_pivot":None},holes=holes,known_at=known,coverage_ok=None if holes else True)
    except (GeometryError,KeyError) as exc:return _invalid("O026",str(exc))


def o027(inp: dict) -> RecipeResult:
    current,baseline=dec(inp.get("current_volume")),dec(inp.get("baseline"))
    if baseline is not None and baseline<=0:return _invalid("O027","baseline must be positive","baseline")
    ratio=None if current is None or baseline is None else current/baseline
    return _r("O027",{"current_volume":current,"baseline_volume":baseline,"rvol":ratio,
        "source_high_rvol":None,"sample_ids":list(inp.get("sample_ids",())),"baseline_statistic":inp.get("baseline_statistic"),
        "known_at":inp.get("window_end")},holes=["HOLE:O027:native_members"],known_at=inp.get("window_end"),coverage_ok=None)


def o028(inp: dict) -> RecipeResult:
    contributors=inp.get("contributors")
    if contributors is None:
        contributors=[{"id":"a","price":dec(inp.get("a")),"confirmed_at":inp.get("a_confirmed_at")},{"id":"b","price":dec(inp.get("b")),"confirmed_at":inp.get("b_confirmed_at")}]
    prices=[dec(item.get("price")) for item in contributors]
    criterion=inp.get("equality_criterion","exact" if inp.get("exact",True) else None);band=inp.get("objective_band",inp.get("band"))
    equal=None
    if criterion=="exact" and all(price is not None for price in prices):equal=len(set(prices))==1
    elif criterion=="source_band" and band is not None:equal=all(dec(band[0])<=price<=dec(band[1]) for price in prices)
    knowns=[item.get("confirmed_at") for item in contributors]
    selection=inp.get("selected_at");use=inp.get("use_at")
    reference_known=all(v is not None for v in knowns) and selection is not None and (use is None or max(*knowns,selection)<=use)
    consumed=inp.get("consumed_at");remaining=None if not reference_known or inp.get("coverage_ok") is not True else consumed is None or use is not None and consumed>use
    holes=[]
    if criterion is None:holes.append("HOLE:O028:equality_criterion")
    if band is None:holes.append("HOLE:O028:objective_band")
    if not reference_known:holes.append("HOLE:O028:availability")
    return _r("O028",{"equal_reference_band":None if band is None else [dec(band[0]),dec(band[1])],
        "contributors":contributors,"prices_equal":equal,"reference_known":reference_known,
        "remaining_objective":remaining,"objective_id":inp.get("objective_id")},holes=holes,known_at=max((v for v in [*knowns,selection] if v is not None),default=None),coverage_ok=None if holes else True)


def o029(inp: dict) -> RecipeResult:
    decision=inp.get("as_of");publication=inp.get("schedule_published_at");release=inp.get("release_known_at");response=inp.get("response_known_at")
    schedule=None if publication is None or decision is None else publication<=decision
    release_known=None if inp.get("actual_release_at") is None or inp.get("vintage_id") is None else release is not None and release<=decision
    new_info=release_known
    source_response=inp.get("source_response") if response is not None and decision is not None and response<=decision else None
    revision=inp.get("thesis_revision_id") if source_response is not None else None
    holes=[]
    if inp.get("event_id") is None or inp.get("timezone") is None:holes.append("HOLE:O029:event_identity")
    if schedule is None:holes.append("HOLE:O029:schedule")
    if release_known is None:holes.append("HOLE:O029:release_time_or_vintage")
    return _r("O029",{"schedule_known":schedule,"release_known":release_known,"new_information_known":new_info,
        "source_response":source_response,"thesis_revision_id":revision,"event_id":inp.get("event_id"),
        "vintage_id":inp.get("vintage_id"),"scheduled_at":inp.get("scheduled_at"),"actual_release_at":inp.get("actual_release_at")},holes=holes,known_at=max((v for v in [publication,release if release_known else None,response if source_response is not None else None] if v is not None),default=None),coverage_ok=None if holes else True)


def o046(inp: dict) -> RecipeResult:
    members = inp.get("members")
    if isinstance(members, list) and members:
        try:
            start, end = inp.get("start_ns"), inp.get("end_ns")
            lows, highs = [], []
            cursor = start
            availability = []
            complete = True
            for member in sorted(members, key=lambda row: row.get("start_ns", row.get("start"))):
                member_start = member.get("start_ns", member.get("start"))
                member_end = member.get("end_ns", member.get("end"))
                if member_start != cursor or member.get("complete") is not True or member.get("coverage_state") not in {"complete", "covered"}:
                    complete = False
                cursor = member_end
                lows.append(_d(member.get("L"), "member low")); highs.append(_d(member.get("H"), "member high"))
                availability.append(member.get("known_at", member_end))
            complete = complete and cursor == end
            low, high = min(lows), max(highs)
            known = max(availability) if all(type(value) is int for value in availability) else None
            box_id = inp.get("box_id", f"local:{start}:{end}")
            holes = [] if complete else ["HOLE:O046:coverage"]
            return _r("O046", {"box_high": high, "box_low": low, "box_width": high-low,
                "box_id": box_id, "formation_start": start, "formation_end": end,
                "known_at": known, "boundary_ids": {"high": f"{box_id}:high", "low": f"{box_id}:low"},
                "source_clock_verified": inp.get("source_clock_verified"), "coverage_ok": True if complete else None,
                "complete": complete, "L": low, "H": high}, holes=holes,
                known_at=known, coverage_ok=True if complete else None)
        except (GeometryError, TypeError, ValueError) as exc:
            return _invalid("O046", str(exc), "members")
    return _r("O046",{"box_high":dec(inp.get("H")),"box_low":dec(inp.get("L")),"box_width":None,
        "box_id":inp.get("box_id"),"formation_start":inp.get("start_ns"),"formation_end":inp.get("end_ns"),
        "known_at":inp.get("known_at"),"boundary_ids":{"high":None,"low":None},
        "source_clock_verified":inp.get("source_clock_verified"),"coverage_ok":None,"complete":False,
        "L":dec(inp.get("L")),"H":dec(inp.get("H"))},holes=["HOLE:O046:native_members"],base_ok=None,coverage_ok=None)


def o047(inp: dict) -> RecipeResult:
    try:
        reference=_d(inp.get("reference_px"),"reference price");side=inp.get("side")
        if side not in {"high","low","upper","lower"}:raise GeometryError("sweep side must be high or low")
        reference_at=inp.get("reference_known_at");decision=inp.get("decision_at",inp.get("use_at"));events=sorted(inp.get("events",()),key=lambda row:row["t"])
        high_side=side in {"high","upper"};sweeps=[row for row in events if (dec(row["price"])>reference if high_side else dec(row["price"])<reference)]
        sweep=sweeps[0] if sweeps else None;extreme=(max((dec(row["price"]) for row in sweeps),default=None) if high_side else min((dec(row["price"]) for row in sweeps),default=None))
        mode=inp.get("confirmation_type");measurement_mode=inp.get("measurement_confirmation_type")
        processing_mode=mode if mode is not None else measurement_mode
        bar=inp.get("confirmation_bar");confirm=None;confirmed=None;close=None;complete_five=None;box_return=None
        if processing_mode in {"complete_close","five_minute_close"}:
            if not isinstance(bar,Mapping) or bar.get("complete") is not True:return _r("O047",{"sweep_at":None if sweep is None else sweep["t"],"sweep_extreme":extreme,"confirm_at":None,"failure_confirmed":None,"reference_known_before_sweep":None if sweep is None or reference_at is None else reference_at<=sweep["t"],"confirmation_type":mode},holes=["HOLE:O047:complete_bar"],known_at=reference_at,coverage_ok=None)
            confirm=bar.get("known_at",bar.get("end"));close=dec(bar.get("C"));other=inp.get("box_other_edge")
            start,end=bar.get("start"),bar.get("end")
            complete_five=None if type(start) is not int or type(end) is not int else end-start==300_000_000_000 and start%300_000_000_000==0
            box_return=None if other is None or close is None else min(reference,dec(other))<close<max(reference,dec(other))
            confirmed=(close<reference if high_side else close>reference)
            if other is not None and inp.get("return_inside_box") is True:
                other=dec(other);confirmed=min(reference,other)<close<max(reference,other)
        elif processing_mode=="supplied_source":
            confirm=inp.get("confirm_at");confirmed=inp.get("source_confirmation")
        if confirm is not None:
            if sweeps and sweeps[0]["t"]>=confirm:return _invalid("O047","sweep does not precede confirmation","ordering")
            sweeps=[row for row in sweeps if row["t"]<confirm]
            sweep=sweeps[0] if sweeps else None
            extreme=(max((dec(row["price"]) for row in sweeps),default=None) if high_side else min((dec(row["price"]) for row in sweeps),default=None))
        retest=next((row for row in events if confirm is not None and row["t"]>confirm and dec(row["price"])==reference),None)
        holes=[]
        if mode is None:holes.append("HOLE:O047:confirmation_type")
        if measurement_mode is not None and mode is None:
            confirmed=None
            holes.append("HOLE:O047:source_confirmation")
        ordering=_ordered(reference_at,None if sweep is None else sweep["t"],confirm,decision,strict=False)
        strict_middle=_ordered(None if sweep is None else sweep["t"],confirm,strict=True)
        if ordering is False or strict_middle is False:return _invalid("O047","reference/sweep/confirmation/decision order is invalid","ordering")
        if sweep is None and inp.get("coverage_ok") is not True:holes.append("HOLE:O047:sweep_coverage")
        if sweep is None and inp.get("coverage_ok") is True:confirmed=False
        if confirm is None:holes.append("HOLE:O047:confirmation")
        return _r("O047",{"sweep_at":None if sweep is None else sweep["t"],"sweep_extreme":extreme,"confirm_at":confirm,
            "failure_confirmed":confirmed,"reference_known_before_sweep":None if sweep is None or reference_at is None else reference_at<=sweep["t"],
            "confirmation_type":mode,"sweep_high":extreme if high_side else None,"sweep_low":extreme if not high_side else None,
            "confirm_close":close,"complete_clock_five_minute_bar":complete_five,"box_return_ok":box_return,
            "retest_at":None if retest is None else retest["t"]},holes=holes,known_at=max((v for v in [confirm,reference_at,None if retest is None else retest["t"]] if v is not None),default=None),coverage_ok=None if holes else True)
    except (GeometryError,KeyError) as exc:return _invalid("O047",str(exc))


def o048(inp: dict) -> RecipeResult:
    return _r("O048",{"prior_high":dec(inp.get("prior_high")),"prior_low":dec(inp.get("prior_low")),
        "period_id":inp.get("period_id"),"period_kind":inp.get("period_kind"),"period_scope":inp.get("period_scope"),
        "period_end":inp.get("period_end"),"known_at":inp.get("known_at"),"active_state":inp.get("active_state"),
        "retirement_policy":inp.get("retirement_policy")},holes=["HOLE:O048:native_members"],base_ok=None,coverage_ok=None)


def o049(inp: dict) -> RecipeResult:
    tdo=dec(inp.get("tdo",inp.get("tdo_price")))
    tdo_known_at=inp.get("tdo_known_at",inp.get("known_at"))
    required=inp.get("tdo_required")
    if required is False:
        result=_r("O049",{"tdo_id":inp.get("tdo_id"),"tdo_price":tdo,"tdo_known_at":tdo_known_at,
            "role":inp.get("role"),"close_through_tdo":None,"close_through_mode":None,"opening_event_id":inp.get("opening_event_id"),
            "source_tdo_close_confirmed":None,"close_completed":None,"distinct":None},known_at=inp.get("known_at"))
        result.applicability="not_required"
        return result
    mode=inp.get("close_through_mode")
    side=inp.get("side")
    if mode is None and side in {"short","long"}:mode="below" if side=="short" else "above"
    close=dec(inp.get("confirmation_close",inp.get("confirm_close")))
    close_through=None if mode not in {"below","above"} or close is None or tdo is None else close<tdo if mode=="below" else close>tdo
    completed=inp.get("complete_clock_five_minute_bar")
    confirmed=None if close is None else bool(completed is True and close_through)
    holes=[]
    if required is True and close is None:holes.append("HOLE:O049:confirm_close")
    if close is not None and completed is None:holes.append("HOLE:O049:close_completed")
    if inp.get("opening_event_id") is None:holes.append("HOLE:O049:opening_event")
    comparisons=[dec(inp.get(name)) for name in ("cash_open","evening_open") if inp.get(name) is not None]
    distinct=None if tdo is None or not comparisons else any(value!=tdo for value in comparisons)
    return _r("O049",{"tdo_id":inp.get("tdo_id"),"tdo_price":tdo,"tdo_known_at":tdo_known_at,
        "role":inp.get("role"),"close_through_tdo":close_through,"close_through_mode":mode,"opening_event_id":inp.get("opening_event_id"),
        "source_tdo_close_confirmed":confirmed,"close_completed":completed,
        "distinct":distinct},
        holes=holes,known_at=inp.get("known_at"),coverage_ok=None if holes else True)


def o050(inp: dict) -> RecipeResult:
    try:
        price=_d(inp.get("open_px"),"cash open");open_at=inp.get("open_at");as_of=inp.get("as_of",inp.get("use_at"));events=sorted(inp.get("events",()),key=lambda row:row["t"])
        eligible=[row for row in events if as_of is None or row["t"]<=as_of]
        below=next((row for row in eligible if dec(row["price"])<price),None);above=next((row for row in eligible if dec(row["price"])>price),None)
        reclaim=next((row for row in eligible if below and row["t"]>below["t"] and dec(row["price"])>price),None)
        known=max((row.get("known_at",row["t"]) for row in eligible),default=open_at)
        holes=["HOLE:O050:confirmation"] if inp.get("source_reclaim_criterion") is None else []
        return _r("O050",{"cash_open":price,"open_event_id":inp.get("open_event_id"),"known_at":known,
            "cross_below_at":None if below is None else below["t"],"cross_above_at":None if above is None else above["t"],
            "source_open_reclaim":None if holes else reclaim is not None,"reclaim_at":None if reclaim is None else reclaim["t"],"as_of":as_of},holes=holes,known_at=known,coverage_ok=inp.get("coverage_ok"))
    except (GeometryError,KeyError) as exc:return _invalid("O050",str(exc))


def o051(inp: dict) -> RecipeResult:
    try:
        friday,sunday=_d(inp.get("friday_close"),"Friday close"),_d(inp.get("sunday_open"),"Sunday open")
        low,high=min(friday,sunday),max(friday,sunday);width=high-low
        direction="up" if sunday>friday else "down" if sunday<friday else "flat"
        events=[dec(row.get("price")) for row in inp.get("events",())]
        if inp.get("price") is not None:events.append(_d(inp.get("price"),"price"))
        partial=any(low<=price<=high for price in events) if events else None
        fill=(any(price<=friday for price in events) if direction=="up" else any(price>=friday for price in events) if direction=="down" else False)
        known=max((v for v in [inp.get("friday_known_at"),inp.get("sunday_known_at"),inp.get("known_at")] if v is not None),default=None)
        holes=[f"HOLE:O051:{key}" for key in ("friday_convention","sunday_convention","gap_id") if inp.get(key) is None]
        return _r("O051",{"gap_lo":low,"gap_hi":high,"gap_width":width,"gap_id":inp.get("gap_id"),"known_at":known,
            "direction":direction,"partial_contact":partial,"full_fill":fill,"objective_selected_at":inp.get("objective_selected_at"),
            "gap":[low,high],"width":width,"entered":partial,"filled":fill,"automatic_gap":width>0},holes=holes,known_at=known,coverage_ok=None if holes else True)
    except GeometryError as exc:return _invalid("O051",str(exc),"endpoints")


def o052(inp: dict) -> RecipeResult:
    try:
        high,low=_d(inp.get("H"),"H"),_d(inp.get("L"),"L");width=high-low
        if width<=0:raise GeometryError("impulse width must be positive")
        side=inp.get("impulse_side")
        if side=="down":band=[low+Decimal(".5")*width,low+Decimal(".618")*width]
        elif side=="up":band=[high-Decimal(".618")*width,high-Decimal(".5")*width]
        else:raise GeometryError("impulse_side must be up or down")
        known=max((v for v in [inp.get("high_confirmed_at"),inp.get("low_confirmed_at"),inp.get("selected_at"),inp.get("known_at")] if v is not None),default=None)
        use=inp.get("use_at")
        if known is not None and use is not None and known>use:return _invalid("O052","impulse selected after band use","ordering")
        holes=[] if inp.get("impulse_id") else ["HOLE:O052:impulse_id"]
        return _r("O052",{"width":width,"band_lo":band[0],"band_hi":band[1],"known_at":known,
            "impulse_id":inp.get("impulse_id"),"impulse_side":side,"linked_failure_id":inp.get("linked_failure_id"),
            "automatic_impulse":None, **_selected_contact(inp,[band])},holes=holes,known_at=known,coverage_ok=None if holes else True)
    except GeometryError as exc:return _invalid("O052",str(exc))


def o053(inp: dict) -> RecipeResult:
    try:
        low,high,price=_d(inp.get("L"),"L"),_d(inp.get("H"),"H"),_d(inp.get("price"),"price")
        width=high-low
        if width<=0:raise GeometryError("selected range width must be positive")
        mid=(high+low)/2;position=(price-low)/width
        location="discount" if price<mid else "premium" if price>mid else "equilibrium"
        vwap=dec(inp.get("vwap"));vrel=None if vwap is None else "below" if price<vwap else "above" if price>vwap else "at"
        holes=[] if inp.get("parent_id") else ["HOLE:O053:parent_id"]
        return _r("O053",{"range_mid":mid,"normalized_position":position,"location":location,
            "parent_id":inp.get("parent_id"),"value_relative_relation":vrel,"value_reference_id":inp.get("value_reference_id")},holes=holes,known_at=max((v for v in [inp.get("known_at"),inp.get("price_known_at")] if v is not None),default=None),coverage_ok=None if holes else True)
    except GeometryError as exc:return _invalid("O053",str(exc),"parent")


def o054(inp: dict) -> RecipeResult:
    failure,swing,brk=inp.get("failure_at"),inp.get("swing_confirmed_at"),inp.get("break_at")
    entry=inp.get("entry_at",inp.get("decision_at"));ordered=_ordered(failure,swing,brk,entry,strict=True)
    same=inp.get("failure_id") is not None and inp.get("failure_id")==inp.get("linked_failure_id",inp.get("failure_id")) and inp.get("episode_id") is not None
    if ordered is False:return _invalid("O054","failure/MSS/entry order is invalid","ordering")
    holes=[]
    for key in ("structure_id","failure_id","break_convention","timeframe"):
        if inp.get(key) is None:holes.append(f"HOLE:O054:{key}")
    supplied=inp.get("source_mss_confirmed")
    confirmed=(supplied is True and ordered is True) if supplied is not None else (None if ordered is None or not same else True)
    # An attributed source observation may preserve its confirmation without
    # pretending the unpublished detector has been implemented.
    if supplied is not None and inp.get("structure_reference") is not None:
        holes=[hole for hole in holes if not hole.endswith(("structure_id","failure_id","break_convention","timeframe"))]
    result=_r("O054",{"structure_reference":inp.get("structure_reference"),"structure_id":inp.get("structure_id"),
        "structure_confirmation_at":brk,"mss_after_failure":confirmed,"automatic_mss":None,
        "linked_gap_id":inp.get("linked_gap_id"),"failure_id":inp.get("failure_id"),"order_ok":ordered},holes=holes,
        state="supplied" if supplied is not None and inp.get("structure_reference") is not None else None,
        known_at=brk,coverage_ok=None if holes else True)
    return result


def o055(inp: dict) -> RecipeResult:
    gap=inp.get("gap");lo=dec(inp.get("gap_lo"));hi=dec(inp.get("gap_hi"))
    if gap is not None and isinstance(gap,(list,tuple)):lo,hi=dec(gap[0]),dec(gap[1])
    if lo is not None and hi is not None and lo>hi:return _invalid("O055","gap bounds are reversed")
    known=inp.get("gap_known_at",inp.get("confirmed_at"));use=inp.get("use_at")
    available=None if known is None or use is None else known<=use
    policy=inp.get("active_policy");active=None
    state_events=sorted(inp.get("state_events",()),key=lambda row:row["known_at"])
    if policy is not None:
        active=True
        for event in state_events:
            if use is None or event["known_at"]<=use:active=event.get("active",active)
    prices=[dec(row.get("price")) for row in inp.get("events",())]
    contact=None if lo is None or hi is None or not prices else any(lo<=price<=hi for price in prices)
    far=inp.get("far_edge");filled=None if far is None or not prices else any(price<=dec(far) for price in prices) if inp.get("direction")=="down" else any(price>=dec(far) for price in prices)
    holes=[]
    for key,value in (("construction",inp.get("construction")),("defining_candle_ids",inp.get("defining_candle_ids")),("active_policy",policy)):
        if value is None:holes.append(f"HOLE:O055:{key}")
    return _r("O055",{"gap_lo":lo,"gap_hi":hi,"gap_known_at":known,"construction":inp.get("construction"),
        "gap_id":inp.get("gap_id"),"defining_candle_ids":list(inp.get("defining_candle_ids",())),
        "active_at_use":active if available is not False else None,"contact_or_fill":{"contact":contact,"full_fill":filled}},holes=holes,known_at=known,coverage_ok=None if holes else True)


def _complete_candle(candle: Mapping[str,Any],name:str)->None:
    if candle.get("complete") is not True or any(candle.get(k) is None for k in ("O","H","L","C","start","end","candle_id")):
        raise GeometryError(f"{name} must be a complete identified candle")


def o056(inp: dict) -> RecipeResult:
    try:
        c1,c2,c3=inp.get("c1"),inp.get("c2"),inp.get("c3")
        for candle,name in ((c1,"C1"),(c2,"C2"),(c3,"C3")):_complete_candle(candle,name)
        if not (c1["end"]<=c2["start"] and c2["end"]<=c3["start"]):raise GeometryError("orderblock candles are not chronological")
        side=inp.get("sweep_side")
        if side=="low":confirmed=dec(c2["L"])<dec(c1["L"]) and dec(c3["C"])>dec(c2["H"])
        elif side=="high":confirmed=dec(c2["H"])>dec(c1["H"]) and dec(c3["C"])<dec(c2["L"])
        else:raise GeometryError("sweep_side must be low or high")
        low,high=dec(c2["L"]),dec(c2["H"]);mode=inp.get("selected_entry_mode");stop=inp.get("selected_stop")
        holes=[]
        if mode not in {"immediate","midpoint","retrace"}:holes.append("HOLE:O056:entry_policy")
        if stop is None:holes.append("HOLE:O056:stop_policy")
        return _r("O056",{"ob_band":[low,high],"ob_mid":(low+high)/2,"confirmation_at":c3["end"],
            "confirmed":confirmed,"sweep_side":side,"selected_entry_mode":mode,"selected_stop":dec(stop),
            "candle_ids":[c1["candle_id"],c2["candle_id"],c3["candle_id"]],"timeframe":inp.get("timeframe")},holes=holes,known_at=c3["end"],coverage_ok=None if holes else True)
    except (GeometryError,TypeError) as exc:return _invalid("O056",str(exc),"candles")


def o057(inp: dict) -> RecipeResult:
    try:
        candle=inp.get("candle") or inp
        for key in ("O","H","L","C"):
            if candle.get(key) is None:raise GeometryError("rejection candle OHLC is incomplete")
        open_,high,low,close=map(dec,(candle["O"],candle["H"],candle["L"],candle["C"]));body_lo=min(open_,close);body_hi=max(open_,close)
        side=inp.get("side","lower")
        band=[low,body_lo] if side=="lower" else [body_hi,high] if side=="upper" else None
        if band is None:raise GeometryError("rejection side must be lower or upper")
        width=band[1]-band[0];holes=[]
        if inp.get("source_rejection") is not True:holes.append("HOLE:O057:source_rejection")
        if inp.get("allowed_location") is not True:holes.append("HOLE:O057:allowed_location")
        if inp.get("stop_policy") is None:holes.append("HOLE:O057:stop_policy")
        return _r("O057",{"body_lo":body_lo,"body_hi":body_hi,"rejection_band":band,"wick_width":width,
            "has_wick":width>0,"known_at":candle.get("end",inp.get("known_at")),"stop_policy":inp.get("stop_policy"),
            "entry_policy":inp.get("entry_policy"),"candle_id":candle.get("candle_id"),"timeframe":inp.get("timeframe")},holes=holes,known_at=candle.get("end",inp.get("known_at")),coverage_ok=None if holes else True)
    except GeometryError as exc:return _invalid("O057",str(exc),"candle")


def _absorption(inp: Mapping[str,Any],bar:Mapping[str,Any],history:Sequence[Mapping[str,Any]])->RecipeResult:
    try:
        if any(bar.get(k) is None for k in ("O","H","L","C","V","end")) or bar.get("complete") is not True:raise GeometryError("current absorption candle is incomplete")
        high,low,open_,close,volume=map(dec,(bar["H"],bar["L"],bar["O"],bar["C"],bar["V"]));width=high-low
        if width<=0:raise GeometryError("absorption candle has zero range")
        complete_history=[row for row in history if row.get("complete") is True]
        identities=[row.get("candle_id") or row.get("bar_id") for row in complete_history]
        present_identities=[identity for identity in identities if identity is not None]
        if len(present_identities)!=len(set(present_identities)):raise GeometryError("absorption history needs unique candle identities")
        evidence_holes=[]
        if bar.get("candle_id") is None and bar.get("bar_id") is None:evidence_holes.append("HOLE:O058:current_candle_identity")
        if any(identity is None for identity in identities):evidence_holes.append("HOLE:O058:history_identity")
        timed=all(type(row.get("start")) is int and type(row.get("end")) is int for row in complete_history)
        current_timed=type(bar.get("start")) is int and type(bar.get("end")) is int
        if not timed or not current_timed:
            evidence_holes.append("HOLE:O058:history_clock")
        else:
            if any(row["end"]>bar["start"] for row in complete_history):raise GeometryError("absorption history overlaps or follows current candle")
            durations={row["end"]-row["start"] for row in complete_history}
            current_duration=bar["end"]-bar["start"]
            if len(durations)>1 or durations and next(iter(durations))!=current_duration:raise GeometryError("absorption history timeframe differs from current candle")
        instruments={str(row.get("instrument_id")) for row in complete_history if row.get("instrument_id") is not None}
        if bar.get("instrument_id") is not None and instruments and instruments!={str(bar["instrument_id"])}:raise GeometryError("absorption history instrument mismatch")
        inclusion=inp.get("average_inclusion");reset=inp.get("reset_policy");equality=inp.get("equality_policy")
        if inclusion not in {None,"prior_only","including_current"}:raise GeometryError("unsupported 14-period average inclusion")
        if reset not in {None,"source","session","continuous"}:raise GeometryError("unsupported absorption reset policy")
        if equality not in {None,"strict","inclusive"}:raise GeometryError("unsupported threshold equality policy")
        prior=sorted(complete_history,key=lambda row:row["end"]) if timed else list(complete_history)
        needed=14 if inclusion in {None,"prior_only"} else 13
        selected_prior=prior[-needed:]
        if len(selected_prior)!=needed:return _r("O058",{"body_ratio":abs(close-open_)/width,"volume_average":None,"volume_ratio":None,
            "small_body":None,"high_volume":None,"source_zone_flag":None,"history_ids":[row.get("candle_id") or row.get("bar_id") for row in prior],
            "thresholds":{"body":"0.6","volume":"1.5","periods":14}},holes=[*evidence_holes,"HOLE:O058:history_14"],known_at=bar["end"],coverage_ok=None)
        if inclusion is None or reset is None or equality is None:
            policy_holes=[f"HOLE:O058:{key}" for key in ("average_inclusion","reset_policy","equality_policy") if inp.get(key) is None]
        else:policy_holes=[]
        average_members=[_d(row.get("V"),"history volume") for row in selected_prior]
        if inclusion=="including_current":average_members.append(volume)
        average=sum(average_members,Decimal(0))/14
        if average<=0:raise GeometryError("volume average must be positive")
        body_ratio=abs(close-open_)/width;volume_ratio=volume/average
        small=body_ratio<Decimal(".6") if body_ratio!=Decimal(".6") else (True if equality=="inclusive" else False if equality=="strict" else None)
        high_volume=volume_ratio>Decimal("1.5") if volume_ratio!=Decimal("1.5") else (True if equality=="inclusive" else False if equality=="strict" else None)
        holes=list(dict.fromkeys([*evidence_holes,*policy_holes]))
        zone=None if small is None or high_volume is None or holes else small and high_volume
        return _r("O058",{"body_ratio":body_ratio,"volume_average":average,"volume_ratio":volume_ratio,
            "small_body":small,"high_volume":high_volume,"source_zone_flag":zone,
            "history_ids":[row.get("candle_id") or row.get("bar_id") for row in selected_prior],"thresholds":{"body":"0.6","volume":"1.5","periods":14}},holes=holes,
            known_at=(max([bar.get("known_at",bar["end"]),*(row.get("known_at") for row in selected_prior)])
                      if all(type(value) is int for value in [bar.get("known_at",bar["end"]),*(row.get("known_at") for row in selected_prior)]) else None),
            coverage_ok=None if holes else True)
    except GeometryError as exc:return _invalid("O058",str(exc),"candle")


def o058(inp: dict) -> RecipeResult:
    bar=inp.get("bar")
    if not isinstance(bar,Mapping):
        bar={key:inp.get(key) for key in ("O","H","L","C","V","start","end","complete","candle_id")}
        bar["complete"]=inp.get("complete",True);bar["end"]=inp.get("known_at")
    # A list of prior volumes supports the printed arithmetic only.  It does
    # not contain candle identity, interval, or availability evidence.
    history=inp.get("history",[{"V":v,"complete":True,"start":None,"end":None,
        "known_at":None,"candle_id":None} for v in inp.get("prior_volumes",())])
    return _absorption(inp,bar,history)


def native_o058(config:Mapping[str,Any],resolved:Any)->RecipeResult:
    rows=sorted((row for row in resolved.rows() if row.get("start") is not None),key=lambda row:row["start"])
    current_id=config.get("current_candle_id");current=next((row for row in rows if row.get("bar_id")==current_id or row.get("candle_id")==current_id),None)
    if current is None:return _invalid("O058","current candle is not among resolved native members","current_candle")
    normalized=[{**row,"candle_id":row.get("candle_id",row.get("bar_id"))} for row in rows]
    current=next(row for row in normalized if row["candle_id"]==current_id)
    names=("average_inclusion","reset_policy","equality_policy")
    if config.get("selection_parent_id") is not None:
        settings=_audited_source_values(config,names)
    elif config.get("variant")=="comparison":
        settings={name:config.get(name) for name in names}
    else:
        settings={name:None for name in names}
    history=[row for row in normalized if row["candle_id"]!=current_id]
    return _absorption(settings,current,history)


def o059(inp: dict) -> RecipeResult:
    necessary=inp.get("necessary_ok");author=inp.get("author");grade=inp.get("source_grade",inp.get("supplied_label"))
    if author=="Green Bird" and grade=="A+" and necessary is False:condition=False
    elif author=="Green Bird" and necessary is True:condition=True
    else:condition=necessary
    holes=[]
    if author=="Green Bird" and necessary is True and grade is None:holes.append("HOLE:O059:sufficient_grade_fields")
    if inp.get("candidate_id") is None:holes.append("HOLE:O059:candidate_identity")
    grade_ok=False if necessary is False else None
    return _r("O059",{"source_grade":grade,"necessary_grade_condition_ok":condition,
        "unpublished_grade_fields":list(inp.get("unpublished_grade_fields",["sufficient_A_plus_criteria"])),
        "grade_known_at":inp.get("grade_known_at",inp.get("known_at")),"selected_exposure":inp.get("selected_exposure"),
        "candidate_id":inp.get("candidate_id"),"grade_ok":grade_ok,"automatic_grade":None,
        "early_is_confirmed_refill":False},holes=holes,known_at=inp.get("grade_known_at",inp.get("known_at")),coverage_ok=None if holes else True)


def o060(inp: dict) -> RecipeResult:
    try:
        lo,hi=_d(inp.get("lo"),"lo"),_d(inp.get("hi"),"hi")
        if lo>hi:raise GeometryError("balance bounds are reversed")
        declared=inp.get("declared_at",inp.get("known_at"));use=inp.get("use_at")
        if declared is not None and use is not None and declared>use:return _invalid("O060","balance declared after use","ordering")
        acceptance=inp.get("source_acceptance");events=sorted(inp.get("migration_events",()),key=lambda row:row["known_at"])
        active=True if acceptance is True else None
        for event in events:
            if use is None or event["known_at"]<=use:active=event.get("active",active)
        holes=[]
        for key in ("auction_id","profile_id","scale"):
            if inp.get(key) is None:holes.append(f"HOLE:O060:{key}")
        if acceptance is None:holes.append("HOLE:O060:source_acceptance")
        holes.append("HOLE:O060:automatic_balance")
        price=dec(inp.get("price"))
        return _r("O060",{"balance_band":[lo,hi],"balance_width":hi-lo,"source_acceptance":acceptance,
            "balance_active_at_use":active,"automatic_balance":None,"auction_id":inp.get("auction_id"),
            "profile_id":inp.get("profile_id"),"scale":inp.get("scale"),"inside":None if price is None else lo<=price<=hi},holes=holes,known_at=declared,coverage_ok=None)
    except GeometryError as exc:return _invalid("O060",str(exc))


def native_o002(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        parent = _native_measurement_parent(config, "reference_parent_id")
        selected_field=config.get("reference_field")
        if selected_field is not None:
            if selected_field not in {"q25","eq","q75"}:raise GeometryError("unsupported named internal reference")
            low=high=_parent_price(parent,selected_field);width=None
        else:
            low, high, width, _ = _reference_bounds(parent, config)
        qualifier = _optional_audited_source_values(config, ("side", "source_criterion",
            "source_reject_evidence", "source_hold_evidence"))
        definition = getattr(resolved, "instrument_definition", None)
        tick = getattr(definition, "tick_size", None)
        rows = resolved.rows()
        events = [{"event_ns": row["event_ns"], "price": row["price"],
                   "sequence": row.get("exchange_sequence")}
                  for row in rows if row.get("action") == "T"]
        bars = [row for row in rows if row.get("start") is not None]
        result = o002({"lo": low, "hi": high, "W": width,
            "side": qualifier.get("side"), "source_criterion": qualifier.get("source_criterion"),
            "source_reject_evidence": qualifier.get("source_reject_evidence"),
            "source_hold_evidence": qualifier.get("source_hold_evidence"),
            "events": events, "bars": bars, "tick_size": tick,
            "tolerance_ticks": config.get("tolerance_ticks"),
            "reference_lineage_id": parent.get("value",{}).get("parent_id",parent.get("value",{}).get("impulse_id",parent["object_id"])),
            "coverage_ok": resolved.coverage_ok, "known_at": resolved.known_at})
        result.evidence_ids = [str(row.get("event_id", row.get("bar_id"))) for row in rows]
        return result
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O002", str(exc), "parents")


def native_o047(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        parent = _native_measurement_parent(config, "reference_parent_id")
        low, high, _, _ = _parent_bounds(parent)
        qualifier = _optional_audited_source_values(config, ("side", "confirmation_type",
            "source_confirmation", "return_inside_box"))
        side = qualifier.get("side")
        measurement_mode = None
        if side is None and config.get("variant") == "comparison":
            side = config.get("measurement_side")
            if side not in {"high", "low"}:
                raise GeometryError("comparison measurement_side must be high or low")
            if config.get("confirmation_bar_parent_id") is None:
                raise GeometryError("comparison failure measurement needs an actual O004 confirmation parent")
            measurement_mode = "complete_close"
        if side in {"high", "upper"}: reference, other, side = high, low, "high"
        elif side in {"low", "lower"}: reference, other, side = low, high, "low"
        else: raise GeometryError("source side must be high or low")
        rows = resolved.rows();bar = _confirmation_bar(config, resolved)
        events = [{"t": row["event_ns"], "price": row["price"], "event_id": row["event_id"]}
                  for row in rows if row.get("action") == "T"]
        result = o047({"reference_px": reference, "reference_known_at": parent.get("known_at"),
            "side": side, "events": events, "confirmation_type": qualifier.get("confirmation_type"),
            "measurement_confirmation_type": measurement_mode,
            "confirmation_bar": bar, "source_confirmation": qualifier.get("source_confirmation"),
            "confirm_at": None if qualifier.get("source_confirmation") is None else config.get("use_at"),
            "box_other_edge": other, "return_inside_box": qualifier.get("return_inside_box"),
            "decision_at": config.get("use_at"), "coverage_ok": resolved.coverage_ok})
        result.evidence_ids = [str(row.get("event_id", row.get("bar_id"))) for row in rows]
        return result
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O047", str(exc), "parents")


def native_o056(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    rows = [{**row, "candle_id": row.get("candle_id", row.get("bar_id"))}
            for row in resolved.rows() if row.get("start") is not None]
    ids = config.get("candle_ids")
    if not isinstance(ids, list) or len(ids) != 3:
        return _invalid("O056", "three explicit candle IDs are required", "candle_ids")
    found = [next((row for row in rows if row["candle_id"] == candle_id), None)
             for candle_id in ids]
    if any(row is None for row in found):
        return _invalid("O056", "identified candle is absent from resolved members", "candles")
    if config.get("selection_parent_id") is not None:
        qualifier = _audited_source_values(config,
            ("sweep_side", "selected_entry_mode", "selected_stop", "timeframe"))
    elif config.get("variant") == "comparison":
        qualifier = {"sweep_side": config.get("measurement_side"),
            "selected_entry_mode": None, "selected_stop": None,
            "timeframe": config.get("measurement_timeframe")}
    else:
        return _invalid("O056", "native pattern needs an audited side selection or comparison measurement", "selection")
    result = o056({**qualifier, "c1": found[0], "c2": found[1], "c3": found[2]})
    result.evidence_ids = list(ids)
    return result


def native_o057(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    candle_id = config.get("candle_id")
    candle = next(({**row, "candle_id": row.get("candle_id", row.get("bar_id"))}
                   for row in resolved.rows() if row.get("bar_id") == candle_id), None)
    if candle is None:
        return _invalid("O057", "identified candle is absent from resolved members", "candle")
    if config.get("selection_parent_id") is not None:
        qualifier = _audited_source_values(config,
            ("side", "source_rejection", "allowed_location", "stop_policy", "entry_policy", "timeframe"))
    elif config.get("variant") == "comparison":
        qualifier = {"side": config.get("measurement_side"), "source_rejection": None,
            "allowed_location": None, "stop_policy": None, "entry_policy": None,
            "timeframe": config.get("measurement_timeframe")}
    else:
        return _invalid("O057", "native rejection geometry needs an audited side selection or comparison measurement", "selection")
    result = o057({**qualifier, "candle": candle})
    result.evidence_ids = [str(candle_id)]
    return result


def _observed_parent(parent: Mapping[str, Any]) -> bool:
    return (parent.get("evidence_class") in {"resolved_native", "parent_derived", "declared_control"}
            or parent.get("state") == "supplied" and bool(parent.get("evidence_ids")))


def _pick_parent(parents: Sequence[Mapping[str, Any]], config: Mapping[str, Any], key: str,
                 *, recipes: Sequence[str] = (), observed: bool = True) -> Mapping[str, Any]:
    identifier = config.get(key)
    matches = [parent for parent in parents if parent.get("object_id") == identifier]
    if identifier is None or len(matches) != 1:
        raise GeometryError(f"{key} must select exactly one actual parent")
    parent = matches[0]
    if recipes and parent.get("recipe_id") not in recipes:
        raise GeometryError(f"{key} selects an incompatible parent recipe")
    if observed and not _observed_parent(parent):
        raise GeometryError(f"{key} lacks native or cited source observations")
    return parent


def _parent_price(parent: Mapping[str, Any], *names: str) -> Decimal:
    value = parent.get("value", {})
    for name in names:
        if value.get(name) is not None:
            return _d(value[name], f"{parent.get('object_id')} {name}")
    raise GeometryError(f"{parent.get('object_id')}: parent price is unavailable")


def _parent_bounds(parent: Mapping[str, Any]) -> tuple[Decimal, Decimal, Decimal, str]:
    value = parent.get("value", {})
    pairs = (("L", "H"), ("box_low", "box_high"), ("on_low", "on_high"),
             ("prior_rth_low", "prior_rth_high"), ("prior_low", "prior_high"),
             ("ibl", "ibh"), ("val", "vah"), ("gap_lo", "gap_hi"),
             ("band_lo", "band_hi"))
    for low_name, high_name in pairs:
        if value.get(low_name) is not None and value.get(high_name) is not None:
            low, high = _d(value[low_name], low_name), _d(value[high_name], high_name)
            if low > high:
                raise GeometryError("parent bounds are reversed")
            identity = (value.get("range_id") or value.get("box_id") or value.get("window_id")
                        or value.get("profile_id") or value.get("ib_id") or value.get("gap_id")
                        or parent.get("object_id"))
            return low, high, high-low, str(identity)
    band = value.get("balance_band", value.get("dealing_band", value.get("band")))
    if isinstance(band, (list, tuple)) and len(band) == 2:
        low, high = _d(band[0], "band low"), _d(band[1], "band high")
        if low > high:
            raise GeometryError("parent band is reversed")
        return low, high, high-low, str(value.get("balance_id", parent.get("object_id")))
    raise GeometryError(f"{parent.get('object_id')}: parent has no typed bounds")


def _reference_bounds(parent: Mapping[str, Any], config: Mapping[str, Any]) -> tuple[Decimal, Decimal, Decimal | None, str]:
    """Resolve a closed range/band or the explicit native VWAP scalar."""
    if parent.get("recipe_id") in {"O030", "O031"}:
        field = "comparison_vwap" if config.get("variant") == "comparison" else "vwap"
        price = _parent_price(parent, field)
        return price, price, None, str(parent.get("object_id"))
    return _parent_bounds(parent)


def _source_values(parent: Mapping[str, Any], names: Sequence[str]) -> dict[str, Any]:
    if not _observed_parent(parent):
        raise GeometryError("source qualifier parent lacks an actual cited observation")
    value = parent.get("value", {})
    return {name: value[name] for name in names if name in value}


def _bar_from_parent(parent: Mapping[str, Any]) -> dict[str, Any]:
    if parent.get("recipe_id") != "O004" or parent.get("evidence_class") != "resolved_native":
        raise GeometryError("candle transform requires a resolved-native O004 parent")
    value = parent.get("value", {})
    required = ("bar_id", "O", "H", "L", "C", "start", "end", "complete")
    if any(value.get(key) is None for key in required):
        raise GeometryError("native candle parent is incomplete")
    if value["complete"] is not True:
        raise GeometryError("native candle parent is not complete")
    return {**{key: value[key] for key in required}, "candle_id": value["bar_id"],
            "V": value.get("V"), "known_at": parent.get("known_at"),
            "timeframe": value.get("size"), "instrument_id": value.get("instrument_id", parent.get("instrument_id"))}


def _native_measurement_parent(config: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    """Select a parent whose values came from native members or closed parents."""
    parent = _pick_parent(list(config.get("parents", {}).values()), config, key)
    if parent.get("evidence_class") not in {"resolved_native", "parent_derived"}:
        raise GeometryError(f"{key} must select a native or parent-derived measurement")
    return parent


def _audited_source_values(config: Mapping[str, Any], names: Sequence[str]) -> dict[str, Any]:
    """Read qualitative settings only from a source-audited parent record."""
    parent = _pick_parent(list(config.get("parents", {}).values()), config, "selection_parent_id")
    if parent.get("state") != "supplied":
        raise GeometryError("selection_parent_id must select an audited supplied source record")
    from ..evidence import source_admitted
    missing = [name for name in names if name in parent.get("value", {})
               and not source_admitted(parent, name)]
    if missing:
        raise GeometryError("source qualifier fields have not passed source audit: " + ", ".join(missing))
    return {name: parent.get("value", {}).get(name) for name in names}


def _optional_audited_source_values(config: Mapping[str, Any], names: Sequence[str]) -> dict[str, Any]:
    """Return only admitted source qualifiers; absence remains explicit unknown."""
    if config.get("selection_parent_id") is None:
        return {name: None for name in names}
    return _audited_source_values(config, names)


def _native_event_key(row: Mapping[str, Any]) -> tuple[int, int, int]:
    sequence = row.get("exchange_sequence")
    return (row["event_ns"], 0 if type(sequence) is int else 1,
            sequence if type(sequence) is int else 0)


def _opening_execution(rows: Sequence[Mapping[str, Any]]) -> tuple[Mapping[str, Any] | None, int | None, list[Mapping[str, Any]]]:
    """Resolve the first execution without inventing order for a tied batch."""
    if not rows:
        return None, None, []
    first_at = min(row["event_ns"] for row in rows)
    batch = [row for row in rows if row["event_ns"] == first_at]
    availability = [row.get("known_at") for row in batch]
    known = max(availability) if all(type(value) is int for value in availability) else None
    if len(batch) == 1:
        return batch[0], known, []
    sequences = [row.get("exchange_sequence") for row in batch]
    if all(type(value) is int for value in sequences) and len(set(sequences)) == len(sequences):
        return min(batch, key=_native_event_key), known, []
    return None, known, batch


def _confirmation_bar(config: Mapping[str, Any], resolved: Any) -> dict[str, Any] | None:
    """Resolve confirmation OHLC from an actual raw bar or O004 parent."""
    parent_id = config.get("confirmation_bar_parent_id")
    raw_id = config.get("confirmation_bar_id")
    if parent_id is not None and raw_id is not None:
        raise GeometryError("confirmation bar must use one evidence route")
    if parent_id is not None:
        parent = _native_measurement_parent(config, "confirmation_bar_parent_id")
        return _bar_from_parent(parent)
    if raw_id is None:
        return None
    matches = [row for row in resolved.rows() if row.get("bar_id") == raw_id]
    if len(matches) != 1:
        raise GeometryError("identified confirmation bar is absent or duplicated")
    row = {**matches[0], "candle_id": matches[0].get("candle_id", raw_id)}
    _complete_candle(row, "confirmation bar")
    return row


def derived_range(recipe_id: str, config: Mapping[str, Any],
                  parents: Sequence[Mapping[str, Any]]) -> RecipeResult:
    """Run a closed transform over explicitly selected trusted parents.

    Configuration selects identities and source policies.  Numeric observations
    and supplied qualitative labels are copied only from the selected parent
    payloads, never from caller summary scalars.
    """
    try:
        inp: dict[str, Any] = {"use_at": config.get("use_at")}
        if recipe_id in {"O007", "O014", "O015", "O052", "O053"}:
            parent = _pick_parent(parents, config, "range_parent_id")
            low, high, width, identity = _parent_bounds(parent)
            inp.update(L=low, H=high, W=width, range_id=identity, parent_id=parent["object_id"],
                       known_at=parent.get("known_at"))
            if parent.get("recipe_coverage_ok") is not True:
                raise GeometryError("projection parent does not have complete frozen coverage")
            if recipe_id == "O014":
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp.update(_source_values(selection, ("k_values", "selected_band", "coordinate_convention_verified", "side")))
                path = config.get("path_parent_id")
                if path is not None:
                    path_parent = _pick_parent(parents, config, "path_parent_id")
                    inp["events"] = list(path_parent.get("value", {}).get("events", ()))
            elif recipe_id == "O015":
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp.update(_source_values(selection, ("coordinate_convention_verified",)))
            elif recipe_id == "O052":
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp.update(_source_values(selection, ("impulse_side", "linked_failure_id", "automatic_impulse")))
                inp["impulse_id"] = parent["object_id"]
            elif recipe_id == "O053":
                price = _pick_parent(parents, config, "price_parent_id")
                inp["price"] = _parent_price(price, "price", "C", "cash_open", "tdo_price")
                inp["price_known_at"] = price.get("known_at")
                value_parent_id = config.get("value_parent_id")
                if value_parent_id is not None:
                    value_parent = _pick_parent(parents, config, "value_parent_id")
                    inp["vwap"] = _parent_price(value_parent, "vwap", "poc", "mpoc")
                    inp["value_reference_id"] = value_parent["object_id"]
            if recipe_id in {"O007","O015","O052"} and config.get("contact_parent_id") is not None:
                contact=_pick_parent(parents,config,"contact_parent_id",recipes=("O002",))
                if contact.get("evidence_class") not in {"resolved_native","parent_derived"}:raise GeometryError("contact must be a native measurement")
                inp["contact_observation"]={**contact["value"],"known_at":contact.get("known_at")}
            result = REGISTRATION_OVERRIDES[recipe_id](inp)
        elif recipe_id == "O008":
            opening = _pick_parent(parents, config, "open_parent_id")
            closing = _pick_parent(parents, config, "close_parent_id")
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(range_open_ref=_parent_price(opening, "O", "cash_open", "tdo_price", "price"),
                       range_close_ref=_parent_price(closing, "C", "price"),
                       anchor_id=selection.get("value", {}).get("anchor_id", selection["object_id"]),
                       reference_verified=selection.get("value", {}).get("reference_verified"),
                       literal_source_label=selection.get("value", {}).get("literal_source_label"),
                       known_at=max(opening["known_at"], closing["known_at"], selection["known_at"])
                       if all(row.get("known_at") is not None for row in (opening, closing, selection)) else None)
            result = o008(inp)
        elif recipe_id == "O009":
            parent = _pick_parent(parents, config, "range_parent_id")
            _, _, width, _ = _parent_bounds(parent)
            inp.update(W=width, known_at=parent.get("known_at"), dependency_known_ats=[parent.get("known_at")])
            if config.get("instrument_parent_id") is not None:
                instrument = _pick_parent(parents, config, "instrument_parent_id")
                inp["tick_size"] = _parent_price(instrument, "tick_size")
                inp["dependency_known_ats"].append(instrument.get("known_at"))
            if config.get("price_parent_id") is not None:
                price = _pick_parent(parents, config, "price_parent_id")
                inp["price_denominator"] = _parent_price(price, "price", "C", "cash_open")
                inp["dependency_known_ats"].append(price.get("known_at"))
            if config.get("prior_range_parent_id") is not None:
                prior = _pick_parent(parents, config, "prior_range_parent_id")
                inp["prior_range_width"] = _parent_bounds(prior)[2]
                inp["dependency_known_ats"].append(prior.get("known_at"))
            if config.get("selection_parent_id") is not None:
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp.update(_source_values(selection, ("source_width_class",)))
                inp["dependency_known_ats"].append(selection.get("known_at"))
            inp["denominator_ids"] = [parent["object_id"], *[str(config[key]) for key in
                ("instrument_parent_id", "price_parent_id", "prior_range_parent_id") if config.get(key) is not None]]
            result = o009(inp)
        elif recipe_id == "O013":
            opening = _pick_parent(parents, config, "open_parent_id")
            prior_value = _pick_parent(parents, config, "prior_value_parent_id")
            prior_range = _pick_parent(parents, config, "prior_range_parent_id")
            inp.update(open_px=_parent_price(opening, "cash_open", "O", "price"), open_at=opening.get("formation_start"),
                       open_known_at=opening.get("known_at"), prior_value=list(_parent_bounds(prior_value)[:2]),
                       prior_range=list(_parent_bounds(prior_range)[:2]),
                       reference_ids=[prior_value["object_id"], prior_range["object_id"]],
                       reference_known_ats=[prior_value.get("known_at"), prior_range.get("known_at")])
            if config.get("current_range_parent_id") is not None:
                current = _pick_parent(parents, config, "current_range_parent_id")
                inp["current_range"] = list(_parent_bounds(current)[:2])
                inp["reference_ids"].append(current["object_id"]); inp["reference_known_ats"].append(current.get("known_at"))
            if config.get("context_parent_id") is not None:
                context = _pick_parent(parents, config, "context_parent_id")
                inp["opening_context"] = dict(context.get("value", {})); inp["rvol_known_at"] = context.get("known_at")
            result = o013(inp)
        elif recipe_id == "O016":
            outer = _pick_parent(parents, config, "outer_parent_id")
            inner = _pick_parent(parents, config, "inner_parent_id")
            outer_l, outer_h, _, _ = _parent_bounds(outer); inner_l, inner_h, _, _ = _parent_bounds(inner)
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(outer_id=outer["object_id"], inner_id=inner["object_id"], outer_L=outer_l, outer_H=outer_h,
                       inner_L=inner_l, inner_H=inner_h,
                       projection_parent_id=config.get("projection_parent_id", inner["object_id"]),
                       known_at=max(outer["known_at"], inner["known_at"], selection["known_at"])
                       if all(row.get("known_at") is not None for row in (outer, inner, selection)) else None)
            inp.update(_source_values(selection, ("source_label", "literal_labels")))
            result = o016(inp)
        elif recipe_id in {"O017", "O018", "O019", "O022", "O023", "O029", "O059", "O060"}:
            source = _pick_parent(parents, config, "source_parent_id")
            inp.update(dict(source.get("value", {})))
            inp["known_at"] = source.get("known_at")
            inp.setdefault("snapshot_known_at", source.get("known_at"))
            if recipe_id == "O060" and config.get("profile_parent_id") is not None:
                profile = _pick_parent(parents, config, "profile_parent_id")
                low, high, _, _ = _parent_bounds(profile)
                inp.update(lo=low, hi=high, profile_id=profile.get("value", {}).get("profile_id"))
            result = REGISTRATION_OVERRIDES[recipe_id](inp)
        elif recipe_id == "O021":
            action = _pick_parent(parents, config, "action_parent_id")
            window = _pick_parent(parents, config, "window_parent_id")
            value = window.get("value", {})
            inp.update(event_ns=action.get("known_at"), window_start=value.get("start_ns", window.get("formation_start")),
                       window_end=value.get("end_ns", window.get("formation_end")))
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(_source_values(selection, ("purpose", "branch", "boundary_convention")))
            result = o021(inp)
        elif recipe_id == "O024":
            attempts = _pick_parent(parents, config, "attempts_parent_id")
            inp.update(attempts=list(attempts.get("value", {}).get("attempts", ())), evaluation_at=config.get("use_at"),
                       level_id=config.get("level_id"), branch=config.get("branch"))
            selection_id = config.get("selection_parent_id")
            if selection_id is not None:
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp.update(_source_values(selection, ("invalidation_evidence_complete", "continuing_through",
                                                        "rejection_absent", "continued_after_failure",
                                                        "prior_allocation", "new_allocation")))
            result = o024(inp)
        elif recipe_id == "O026":
            low = _pick_parent(parents, config, "low_parent_id")
            high = _pick_parent(parents, config, "high_parent_id")
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(low=_parent_price(low, "price", "L", "C"), high=_parent_price(high, "price", "H", "C"),
                       low_id=low["object_id"], high_id=high["object_id"], low_confirmed_at=low.get("known_at"),
                       high_confirmed_at=high.get("known_at"), swing_id=selection.get("value", {}).get("swing_id", selection["object_id"]))
            inp.update(_source_values(selection, ("timeframe",)))
            result = o026(inp)
        elif recipe_id == "O028":
            requested = config.get("contributor_parent_ids")
            if not isinstance(requested, list) or len(requested) < 2 or len(set(requested)) != len(requested):
                raise GeometryError("equal reference needs at least two distinct contributor parents")
            contributors = []
            for identifier in requested:
                parent = _pick_parent(parents, {"id": identifier}, "id")
                contributors.append({"id": identifier, "price": _parent_price(parent, "price", "H", "L", "poc"),
                                     "confirmed_at": parent.get("known_at")})
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(contributors=contributors, selected_at=selection.get("known_at"), coverage_ok=True)
            inp.update(_source_values(selection, ("equality_criterion", "objective_band", "objective_id", "consumed_at")))
            result = o028(inp)
        elif recipe_id == "O051":
            friday = _pick_parent(parents, config, "friday_close_parent_id")
            sunday = _pick_parent(parents, config, "sunday_open_parent_id")
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(friday_close=_parent_price(friday, "C", "price"), sunday_open=_parent_price(sunday, "O", "price"),
                       friday_known_at=friday.get("known_at"), sunday_known_at=sunday.get("known_at"))
            inp.update(_source_values(selection, ("friday_convention", "sunday_convention", "gap_id", "objective_selected_at")))
            if config.get("price_parent_id") is not None:
                price = _pick_parent(parents, config, "price_parent_id")
                inp["price"] = _parent_price(price, "price", "C")
            result = o051(inp)
        elif recipe_id == "O054":
            failure = _pick_parent(parents, config, "failure_parent_id")
            swing = _pick_parent(parents, config, "swing_parent_id")
            breakout = _pick_parent(parents, config, "break_parent_id")
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(failure_at=failure.get("known_at"), swing_confirmed_at=swing.get("known_at"),
                       break_at=breakout.get("known_at"), entry_at=config.get("use_at"),
                       failure_id=failure["object_id"], linked_failure_id=failure["object_id"],
                       structure_id=swing["object_id"], episode_id=config.get("episode_id", failure["object_id"]))
            inp.update(_source_values(selection, ("structure_reference", "source_mss_confirmed", "break_convention",
                                                    "timeframe", "linked_gap_id")))
            result = o054(inp)
        elif recipe_id == "O055":
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(_source_values(selection, ("gap", "gap_lo", "gap_hi", "construction", "gap_id",
                                                    "active_policy", "far_edge", "direction", "state_events")))
            candle_ids = config.get("defining_candle_parent_ids")
            if not isinstance(candle_ids, list) or not candle_ids:
                raise GeometryError("gap requires its actual defining candle parents")
            candles = [_pick_parent(parents, {"id": identifier}, "id", recipes=("O004",)) for identifier in candle_ids]
            inp["defining_candle_ids"] = [candle["value"]["bar_id"] for candle in candles]
            inp["gap_known_at"] = max(candle["known_at"] for candle in candles) if all(candle.get("known_at") is not None for candle in candles) else None
            result = o055(inp)
        elif recipe_id in {"O056", "O057", "O058"}:
            if recipe_id == "O056":
                ids = config.get("candle_parent_ids")
                if not isinstance(ids, list) or len(ids) != 3 or len(set(ids)) != 3:
                    raise GeometryError("orderblock requires three distinct candle parent IDs")
                candles = [_bar_from_parent(_pick_parent(parents, {"id": identifier}, "id", recipes=("O004",))) for identifier in ids]
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp.update(c1=candles[0], c2=candles[1], c3=candles[2])
                inp.update(_source_values(selection, ("sweep_side", "selected_entry_mode", "selected_stop", "timeframe")))
                result = o056(inp)
            elif recipe_id == "O057":
                candle = _bar_from_parent(_pick_parent(parents, config, "candle_parent_id", recipes=("O004",)))
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp["candle"] = candle
                inp.update(_source_values(selection, ("side", "source_rejection", "allowed_location", "stop_policy", "entry_policy", "timeframe")))
                result = o057(inp)
            else:
                current = _bar_from_parent(_pick_parent(parents, config, "current_candle_parent_id", recipes=("O004",)))
                history_ids = config.get("history_candle_parent_ids")
                if not isinstance(history_ids, list) or len(history_ids) != 14 or len(set(history_ids)) != 14:
                    raise GeometryError("absorption needs exactly fourteen distinct prior candle parents")
                history = [_bar_from_parent(_pick_parent(parents, {"id": identifier}, "id", recipes=("O004",))) for identifier in history_ids]
                selection = _pick_parent(parents, config, "selection_parent_id")
                inp.update(bar=current, history=history)
                inp.update(_source_values(selection, ("average_inclusion", "reset_policy", "equality_policy")))
                result = o058(inp)
        else:
            raise GeometryError(f"{recipe_id}: no closed parent transform")
        result.parent_ids = [parent["object_id"] for parent in parents]
        return result
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid(recipe_id, str(exc), "parents")


def native_o010(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        parent = _pick_parent(list(config.get("parents", {}).values()), config, "range_parent_id")
        low, high, _, _ = _parent_bounds(parent)
        events = [{"t": row["event_ns"], "price": row["price"], "event_id": row.get("event_id")}
                  for row in resolved.rows() if row.get("action") == "T" and row.get("event_ns") is not None]
        result = o010({"L": low, "H": high, "events": events,
            "window_start": resolved.start_ns, "window_end": resolved.end_ns,
            "as_of": config.get("as_of", resolved.end_ns), "coverage_ok": resolved.coverage_ok,
            "known_at": resolved.known_at})
        result.evidence_ids = [str(row["event_id"]) for row in resolved.rows() if row.get("event_id") is not None]
        return result
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O010", str(exc), "parents")


def native_o012(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        parent = _pick_parent(list(config.get("parents", {}).values()), config, "reference_parent_id")
        value = parent.get("value", {})
        side = config.get("side")
        price = (_parent_price(parent, "H", "box_high", "prior_high", "poc") if side == "high"
                 else _parent_price(parent, "L", "box_low", "prior_low", "poc"))
        events = [{"t": row["event_ns"], "price": row["price"], "known_at": row.get("known_at"),
                   "session": config.get("session_classifier", "all")}
                  for row in resolved.rows() if row.get("action") == "T"]
        result = o012({**config, "reference_px": price, "reference_id": parent["object_id"],
            "reference_known_at": parent.get("known_at"), "events": events,
            "coverage_ok": resolved.coverage_ok})
        result.evidence_ids = [str(row.get("event_id")) for row in resolved.rows() if row.get("event_id") is not None]
        return result
    except (GeometryError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O012", str(exc), "parents")


REGISTRATION_OVERRIDES = {
    rid: globals()[rid.lower()] for rid in
    ["O002", *[f"O{i:03}" for i in range(5, 30)], *[f"O{i:03}" for i in range(46, 61)]]
}

NATIVE_PRODUCERS = {
    "O002": native_o002, "O005": native_o005, "O006": native_o006,
    "O010": native_o010, "O011": native_o011, "O012": native_o012,
    "O020": native_o020, "O025": native_o025,
    "O027": native_o027, "O046": native_o046, "O047": native_o047,
    "O048": native_o048, "O049": native_o049, "O050": native_o050,
    "O056": native_o056, "O057": native_o057, "O058": native_o058,
}

_DERIVED_IDS = {
    "O007", "O008", "O009", "O013", "O014", "O015", "O016", "O017",
    "O018", "O019", "O021", "O022", "O023", "O024", "O026", "O028",
    "O029", "O051", "O052", "O053", "O054", "O055", "O056", "O057",
    "O058", "O059", "O060",
}
DERIVED_PRODUCERS = {
    recipe_id: (lambda config, parents, recipe_id=recipe_id:
                derived_range(recipe_id, config, parents))
    for recipe_id in _DERIVED_IDS
}

REQUIRED_INPUTS = {
    "O002": ("lo", "hi"), "O005": (), "O006": (), "O007": ("L", "H"),
    "O008": (), "O009": ("W",), "O010": ("H", "L", "events"), "O011": (),
    "O012": ("reference_px", "reference_known_at", "side"), "O013": ("open_px",),
    "O014": ("L", "H"), "O015": ("L", "H"), "O016": ("outer_L", "outer_H"),
    "O017": (), "O018": (), "O019": ("lo", "hi"), "O020": (),
    "O021": ("event_ns",), "O022": ("label", "recorded_at"), "O023": (),
    "O024": ("attempts",), "O025": (),
    "O026": ("low", "high", "low_confirmed_at", "high_confirmed_at"),
    "O027": (), "O028": (), "O029": ("as_of",),
    "O046": (), "O047": ("reference_px", "side"), "O048": (), "O049": (),
    "O050": ("open_px", "open_at"), "O051": ("friday_close", "sunday_open"),
    "O052": ("H", "L", "impulse_side"), "O053": ("L", "H", "price"),
    "O054": ("failure_at", "swing_confirmed_at", "break_at"), "O055": (),
    # O056 is side-symmetric: neither c1_l nor c1_h is a universal field.
    "O056": ("c1", "c2", "c3", "sweep_side"),
    "O057": ("O", "H", "L", "C"), "O058": ("O", "H", "L", "C", "V"),
    "O059": ("necessary_ok",), "O060": ("lo", "hi"),
}


F = OutputField


def _fields(**items: tuple[tuple[type, ...], bool]) -> dict[str, OutputField]:
    return {name: F(types, nullable) for name, (types, nullable) in items.items()}


D = (Decimal,); I = (int,); S = (str,); B = (bool,); LST = (list,); MAP = (dict,)
N_D=(D,True); N_I=(I,True); N_S=(S,True); N_B=(B,True)

OUTPUT_SCHEMAS = {
    "O002": _fields(contact_at=N_I, price_overlap=N_B, strict_break_side=N_S,
        sweep_depth=N_D, sweep_depth_ticks=N_D, literal_close_return=N_B,
        source_reject=N_B, source_hold=N_B, tolerance_ticks=N_D,observed_high=N_D,observed_low=N_D,reference_band=(LST,True),reference_lineage_id=N_S),
    "O005": _fields(range_id=(S,False), instrument_id=((str,int),False), source_clock_id=(S,False),
        L=(D,False), H=(D,False), W=(D,False), formation_start=(I,False), formation_end=(I,False),
        known_at=N_I, range_known_at=N_I, range_frozen=(B,False), coverage_ok=N_B,
        member_ids=(LST,False), parent_id=N_S),
    "O006": _fields(source_clock_id=(S,False), range_id=(S,False), instrument_id=((str,int),False),
        L=(D,False), H=(D,False), W=(D,False), formation_start=(I,False), formation_end=(I,False),
        known_at=N_I, range_known_at=N_I, range_frozen=(B,False), coverage_ok=N_B,
        member_ids=(LST,False), parent_id=N_S, source_clock_verified=N_B),
    "O007": _fields(parent_id=N_S,q25=(D,False),eq=(D,False),q75=(D,False),selected_contact=N_B,selected_contact_at=N_I),
    "O008": _fields(range_open_ref=N_D,range_close_ref=N_D,anchor_id=N_S,reference_verified=N_B,
        directed_path=N_B,literal_source_label=N_S),
    "O009": _fields(width_points=(D,False),width_ticks=N_D,price_percent=N_D,width_ratio=N_D,
        source_width_class=((str,bool),True),denominator_ids=(LST,False)),
    "O010": _fields(high_break_at=N_I,low_break_at=N_I,path=(S,False),first_side=N_S,
        eq_return_at=N_I,window_complete=(B,False)),
    "O011": _fields(on_high=(D,False),on_low=(D,False),on_width=(D,False),window_id=(S,False),
        known_at=N_I,formation_start=(I,False),formation_end=(I,False),instrument_id=((str,int),False),
        coverage_ok=N_B,member_ids=(LST,False)),
    "O012": _fields(reference_id=N_S,active_before_use=N_B,purged_at=N_I,consumption_scope=N_S,
        purge_known_at=N_I,source_purged_context=N_B,rth_exception_applied=(B,False)),
    "O013": _fields(open_vs_value=N_S,open_vs_range=N_S,open_vs_current_range=N_S,
        opening_context=((str,dict),True),rvol_known_at=N_I,open_at=N_I,reference_ids=(LST,False)),
    "O014": _fields(upper_ladder=(MAP,False),lower_ladder=(MAP,False),selected_band=((list,tuple),True),
        sweep_depth_points=N_D,sweep_depth_W=N_D,touch_at=N_I,parent_id=N_S),
    "O015": _fields(upper_band=(LST,False),lower_band=(LST,False),parent_id=N_S,known_at=N_I,selected_contact=N_B,selected_contact_at=N_I),
    "O016": _fields(outer_id=N_S,inner_id=N_S,outer_width=(D,False),inner_width=N_D,
        outer_mid=(D,False),inner_mid=N_D,parent_binding=N_S,inner_geometry_known=N_B,
        automatic_inner_span=((dict,list),True),literal_labels=(LST,False)),
    "O017": _fields(average_hi=N_D,average_lo=N_D,median_hi=N_D,median_lo=N_D,
        min_average_hi=N_D,min_average_lo=N_D,midpoint_when_labeled=N_D,midpoint_parent=N_S,
        source_band_known=N_B,automatic_bands=((dict,list),True),settings=(MAP,True)),
    "O018": _fields(ev_low=N_D,ev_high=N_D,ev_mid_if_supplied=N_D,ev_reference_known=N_B,
        automatic_ev=((dict,list),True),ev_id=N_S,anchor_id=N_S,source_version=N_S),
    "O019": _fields(pzone_id=N_S,lo=(D,False),hi=(D,False),anchor_at=N_I,source_zone_known=N_B,
        active_at_use=N_B,directed_path_recorded=N_B,source_id=N_S,target_id=N_S,settings=(MAP,True)),
    "O020": _fields(prior_rth_high=(D,False),prior_rth_low=(D,False),prior_range_id=(S,False),known_at=N_I,
        rth_active_objectives=(LST,False),chosen_draw=((str,dict),True),current_direction=N_S,coverage_ok=N_B),
    "O021": _fields(at_rth_open=(B,False),source_time_window=N_B,exit_window_recorded=(B,False),
        actual_action_at=(I,False),purpose=N_S,branch=N_S,boundary_ambiguous=(B,False)),
    "O022": _fields(source_cleanliness_label=N_S,session_selected_before_use=N_B,
        automatic_cleanliness=((str,bool),True),session_id=N_S,reason=N_S),
    "O023": _fields(phase_label=N_S,phase_known_at=N_I,used_as_context=(B,False),
        transition_sequence=N_B,automatic_phase=((str,dict),True),contemporaneous=N_B),
    "O024": _fields(failed_attempt_count=(I,False),failed_attempt_ids=(LST,False),three_failed_attempts=(B,False),
        reversal_invalidated=N_B,later_allocation_ok=N_B),
    "O025": _fields(or_mid=N_D,or_high=N_D,or_low=N_D,or_id=N_S,or_known=N_B,
        subsequent_mid_retrace=N_I,known_at=N_I),
    "O026": _fields(swing_mid=(D,False),swing_known_at=(I,False),later_mid_contact=N_I,
        swing_id=N_S,endpoint_ids=(LST,False),automatic_pivot=((dict,bool),True)),
    "O027": _fields(current_volume=N_D,baseline_volume=N_D,rvol=N_D,source_high_rvol=N_B,
        sample_ids=(LST,False),baseline_statistic=N_S,known_at=N_I),
    "O028": _fields(equal_reference_band=((list,tuple),True),contributors=(LST,False),prices_equal=N_B,
        reference_known=(B,False),remaining_objective=N_B,objective_id=N_S),
    "O029": _fields(schedule_known=N_B,release_known=N_B,new_information_known=N_B,
        source_response=((str,dict),True),thesis_revision_id=N_S,event_id=N_S,vintage_id=N_S,
        scheduled_at=N_I,actual_release_at=N_I),
    "O046": _fields(box_high=(D,False),box_low=(D,False),box_width=(D,False),box_id=(S,False),
        formation_start=(I,False),formation_end=(I,False),known_at=N_I,boundary_ids=(MAP,False),
        source_clock_verified=N_B,coverage_ok=N_B),
    "O047": _fields(sweep_at=N_I,sweep_extreme=N_D,confirm_at=N_I,failure_confirmed=N_B,
        reference_known_before_sweep=N_B,confirmation_type=N_S,sweep_high=N_D,sweep_low=N_D,confirm_close=N_D,complete_clock_five_minute_bar=N_B,box_return_ok=N_B,retest_at=N_I),
    "O048": _fields(prior_high=(D,False),prior_low=(D,False),period_id=N_S,period_kind=N_S,
        period_scope=N_S,period_end=N_I,known_at=N_I,active_state=N_B,retirement_policy=N_S),
    "O049": _fields(tdo_id=N_S,tdo_price=N_D,tdo_known_at=N_I,role=N_S,
        close_through_tdo=N_B,close_through_mode=N_S,opening_event_id=N_S),
    "O050": _fields(cash_open=N_D,open_event_id=N_S,known_at=N_I,cross_below_at=N_I,
        cross_above_at=N_I,source_open_reclaim=N_B,reclaim_at=N_I,as_of=N_I),
    "O051": _fields(gap_lo=(D,False),gap_hi=(D,False),gap_width=(D,False),gap_id=N_S,known_at=N_I,
        direction=(S,False),partial_contact=N_B,full_fill=(B,False),objective_selected_at=N_I,
        gap=(LST,False),width=(D,False),entered=N_B,filled=(B,False),automatic_gap=(B,False)),
    "O052": _fields(width=(D,False),band_lo=(D,False),band_hi=(D,False),known_at=N_I,
        impulse_id=N_S,impulse_side=(S,False),linked_failure_id=N_S,automatic_impulse=((dict,bool),True),selected_contact=N_B,selected_contact_at=N_I),
    "O053": _fields(range_mid=(D,False),normalized_position=(D,False),location=(S,False),
        parent_id=(S,False),value_relative_relation=N_S,value_reference_id=N_S),
    "O054": _fields(structure_reference=((str,dict,Decimal),True),structure_id=N_S,structure_confirmation_at=N_I,
        mss_after_failure=N_B,automatic_mss=((dict,bool),True),linked_gap_id=N_S,failure_id=N_S,order_ok=N_B),
    "O055": _fields(gap_lo=N_D,gap_hi=N_D,gap_known_at=N_I,construction=N_S,gap_id=N_S,
        defining_candle_ids=(LST,False),active_at_use=N_B,contact_or_fill=(MAP,False)),
    "O056": _fields(ob_band=(LST,False),ob_mid=(D,False),confirmation_at=(I,False),confirmed=(B,False),
        sweep_side=(S,False),selected_entry_mode=N_S,selected_stop=N_D,candle_ids=(LST,False),timeframe=N_S),
    "O057": _fields(body_lo=(D,False),body_hi=(D,False),rejection_band=(LST,False),wick_width=(D,False),
        has_wick=(B,False),known_at=N_I,stop_policy=((str,dict),True),entry_policy=((str,dict),True),
        candle_id=N_S,timeframe=N_S),
    "O058": _fields(body_ratio=N_D,volume_average=N_D,volume_ratio=N_D,small_body=N_B,high_volume=N_B,
        source_zone_flag=N_B,history_ids=(LST,False),thresholds=(MAP,False)),
    "O059": _fields(source_grade=N_S,necessary_grade_condition_ok=N_B,unpublished_grade_fields=(LST,False),
        grade_known_at=N_I,selected_exposure=((str,Decimal,dict),True),candidate_id=N_S,
        grade_ok=N_B,automatic_grade=((str,bool,dict),True),early_is_confirmed_refill=(B,False)),
    "O060": _fields(balance_band=(LST,False),balance_width=(D,False),source_acceptance=N_B,
        balance_active_at_use=N_B,automatic_balance=((dict,list),True),auction_id=N_S,
        profile_id=N_S,scale=N_S,inside=N_B),
}


__all__ = ["DERIVED_PRODUCERS", "GeometryError", "NATIVE_PRODUCERS", "OUTPUT_SCHEMAS",
           "REGISTRATION_OVERRIDES", "REQUIRED_INPUTS", "RangeGeometry",
           "build_native_range"]
