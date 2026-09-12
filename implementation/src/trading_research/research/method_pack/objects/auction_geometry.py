"""Dated TPO and auction-route objects for Phase 1.

The module separates geometry that can be computed from covered native members
from author observations whose detector is not published.  Unknown source
criteria therefore remain nullable fields with named holes; they are never
replaced by convenient duration, distance, or direction defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

from trading_research.research.method_pack.clocks import et_ns, ns_to_et
from trading_research.research.method_pack.contracts import OutputField
from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult


HALF_HOUR_NS = 30 * 60 * 1_000_000_000
RTH_END_NS_FROM_OPEN = 13 * HALF_HOUR_NS


class AuctionError(ValueError):
    pass


@dataclass(frozen=True)
class TPOProfile:
    profile_id: str
    instrument_id: str | int
    instrument_definition_id: str
    session_date_et: str
    price_step: Decimal
    construction: str
    as_of: int
    known_at: int
    memberships: tuple[tuple[Decimal, tuple[str, ...]], ...]
    period_ranges: tuple[tuple[str, Decimal, Decimal, int, int], ...]
    completed_periods: tuple[str, ...]
    coverage_ok: bool | None
    event_ids: tuple[str, ...]


def _d(value: Any, name: str) -> Decimal:
    result = dec(value)
    if result is None or not result.is_finite():
        raise AuctionError(f"{name} is required")
    return result


def _t(value: Any, name: str) -> int:
    if type(value) is not int:
        raise AuctionError(f"{name} must be an integer event key")
    return value


def _nullable_bool(value: Any, name: str) -> bool | None:
    if value is not None and type(value) is not bool:
        raise AuctionError(f"{name} must be nullable Boolean")
    return value


def _r(rid: str, value: dict[str, Any], *, holes: Sequence[str] = (),
       known_at: int | None = None, state: str | None = None,
       base_ok: bool | None = True, coverage_ok: bool | None = True,
       reason: str | None = None, parent_ids: Sequence[str] = (),
       evidence_ids: Sequence[str] = ()) -> RecipeResult:
    unique = list(dict.fromkeys(holes))
    return RecipeResult(
        rid, state or ("computed" if not unique else "hole"), value, unique,
        known_at=known_at, base_ok=base_ok, coverage_ok=coverage_ok,
        reason=reason, parent_ids=list(parent_ids), evidence_ids=list(evidence_ids),
    )


def _invalid(rid: str, message: str, field: str = "evidence") -> RecipeResult:
    return _r(rid, {}, holes=[f"HOLE:{rid}:{field}"], state="invalid",
              base_ok=False, coverage_ok=None, reason=message)


def _holes(rid: str, inp: Mapping[str, Any], required: Iterable[str]) -> list[str]:
    return [f"HOLE:{rid}:{key}" for key in required if inp.get(key) is None]


def _known(*values: Any) -> int | None:
    present = [value for value in values if type(value) is int]
    return max(present) if present else None


def _order(*values: Any, strict: bool = True) -> bool | None:
    if any(type(value) is not int for value in values):
        return None
    return all(a < b if strict else a <= b for a, b in zip(values, values[1:]))


def _side(value: Any, name: str = "side") -> str:
    aliases = {"up": "long", "down": "short", "upper": "high", "lower": "low"}
    result = aliases.get(value, value)
    if result not in {"long", "short", "high", "low", "above", "below"}:
        raise AuctionError(f"invalid {name}")
    return result


def _session_open(session_date: Any) -> int:
    if hasattr(session_date, "isoformat"):
        day = session_date
    elif isinstance(session_date, str):
        from datetime import date
        day = date.fromisoformat(session_date)
    else:
        raise AuctionError("session_date_et is required")
    return et_ns(day, 9, 30)


def _letter(index: int) -> str:
    if not 0 <= index < 26:
        raise AuctionError("TPO period index is outside the supported RTH alphabet")
    return chr(ord("A") + index)


def _row_map(value: Any) -> dict[Decimal, set[str]]:
    if isinstance(value, TPOProfile):
        return {price: set(letters) for price, letters in value.memberships}
    if not isinstance(value, Mapping):
        raise AuctionError("TPO memberships are required")
    rows: dict[Decimal, set[str]] = {}
    for price, letters in value.items():
        if not isinstance(letters, (list, tuple, set, frozenset)):
            raise AuctionError("each TPO row must retain its letter set")
        rows[_d(price, "TPO price")] = {str(letter) for letter in letters}
    return rows


def _on_grid(price: Decimal, step: Decimal, origin: Decimal) -> bool:
    return ((price - origin) / step) == ((price - origin) / step).to_integral_value()


def _expand_grid(low: Decimal, high: Decimal, step: Decimal) -> list[Decimal]:
    if high < low:
        raise AuctionError("period range is reversed")
    span = (high - low) / step
    if span != span.to_integral_value():
        raise AuctionError("period range is not aligned to the selected price step")
    return [low + step * index for index in range(int(span) + 1)]


def build_tpo_profile(*, profile_id: str, instrument_id: str | int,
                      instrument_definition_id: str, session_date_et: Any,
                      price_step: Any, construction: str, observations: Sequence[Mapping[str, Any]],
                      as_of: int, coverage_ok: bool | None,
                      period_coverage: Mapping[str, bool | None] | None = None,
                      grid_origin: Any = 0) -> TPOProfile:
    """Build an immutable TPO snapshot from one selected visitation convention."""

    if construction not in {"trade_visited", "period_range"}:
        raise AuctionError("source TPO construction must be trade_visited or period_range")
    step, origin = _d(price_step, "price_step"), _d(grid_origin, "grid_origin")
    if step <= 0:
        raise AuctionError("price_step must be positive")
    opening = _session_open(session_date_et)
    if not opening <= as_of <= opening + RTH_END_NS_FROM_OPEN:
        raise AuctionError("TPO as_of is outside the dated RTH session")

    members: dict[Decimal, set[str]] = {}
    ranges: dict[str, list[Any]] = {}
    range_members: dict[str, list[tuple[int, int, Decimal, Decimal, int, str]]] = {}
    source_coverage = coverage_ok
    event_ids: list[str] = []
    availability: list[int] = []
    for row in observations:
        at = row.get("event_ns", row.get("t", row.get("start", row.get("start_ns"))))
        if type(at) is not int or at > as_of or at < opening:
            continue
        index = (at - opening) // HALF_HOUR_NS
        if not 0 <= index < 13:
            continue
        label = _letter(int(index))
        start, end = opening + index * HALF_HOUR_NS, opening + (index + 1) * HALF_HOUR_NS
        supplied = row.get("letter", row.get("period_id"))
        if supplied is not None:
            supplied_label = str(supplied).split(":")[-1]
            if supplied_label != label:
                raise AuctionError("supplied letter does not match the dated 30-minute period")
        if construction == "trade_visited":
            if row.get("action", "T") != "T":
                continue
            low = high = _d(row.get("price"), "trade price")
            available = row.get("known_at", at)
            if type(available) is not int or available > as_of:
                continue
            if not _on_grid(low, step, origin):
                raise AuctionError("trade price is off the selected TPO grid")
            prices = [low]
        else:
            row_start = row.get("start", row.get("start_ns"))
            row_end = row.get("end", row.get("end_ns"))
            if type(row_start) is not int or type(row_end) is not int or row_end <= row_start:
                raise AuctionError("period-range member needs a positive exact interval")
            if row_start < start or row_end > end:
                raise AuctionError("period-range member crosses a dated 30-minute boundary")
            low = _d(row.get("L", row.get("low")), "period low")
            high = _d(row.get("H", row.get("high")), "period high")
            available = row.get("known_at", row_end)
            if (row.get("complete") is not True or row_end > as_of
                    or type(available) is not int or available > as_of):
                continue
            if high < low:
                raise AuctionError("period range is reversed")
            event_id = str(row.get("event_id", row.get("bar_id", f"{label}:{row_start}")))
            range_members.setdefault(label, []).append(
                (row_start, row_end, low, high, available, event_id))
            continue
        for price in prices:
            members.setdefault(price, set()).add(f"{session_date_et}:{label}")
        if label not in ranges:
            ranges[label] = [low, high, start, end]
        else:
            ranges[label][0] = min(ranges[label][0], low)
            ranges[label][1] = max(ranges[label][1], high)
        event_ids.append(str(row.get("event_id", row.get("bar_id", f"{label}:{at}"))))
        if type(available) is int:
            availability.append(available)

    if construction == "period_range":
        elapsed_periods: list[str] = []
        for index in range(13):
            label = _letter(index)
            start = opening + index * HALF_HOUR_NS
            end = start + HALF_HOUR_NS
            if end > as_of:
                break
            elapsed_periods.append(label)
            selected = sorted(range_members.get(label, ()), key=lambda item: (item[0], item[1]))
            cursor = start
            complete_members: list[tuple[int, int, Decimal, Decimal, int, str]] = []
            for item in selected:
                row_start, row_end = item[0], item[1]
                if row_start != cursor:
                    complete_members = []
                    break
                cursor = row_end
                complete_members.append(item)
            complete = source_coverage is True and cursor == end and bool(complete_members)
            if period_coverage is not None:
                complete = complete and period_coverage.get(label) is True
            if not complete:
                continue
            low = min(item[2] for item in complete_members)
            high = max(item[3] for item in complete_members)
            for price in _expand_grid(low, high, step):
                members.setdefault(price, set()).add(f"{session_date_et}:{label}")
            ranges[label] = [low, high, start, end]
            event_ids.extend(item[5] for item in complete_members)
            availability.extend(item[4] for item in complete_members)
        if source_coverage is True and any(label not in ranges for label in elapsed_periods):
            coverage_ok = None

    completed: list[str] = []
    period_rows: list[tuple[str, Decimal, Decimal, int, int]] = []
    for index in range(13):
        label = _letter(index)
        end = opening + (index + 1) * HALF_HOUR_NS
        if end > as_of:
            break
        complete = source_coverage is True
        if period_coverage is not None:
            complete = period_coverage.get(label) is True
        if label in ranges and complete:
            completed.append(label)
            lo, hi, start, _ = ranges[label]
            period_rows.append((label, lo, hi, start, end))
    known = max([as_of, *availability])
    return TPOProfile(
        str(profile_id), instrument_id, str(instrument_definition_id),
        str(session_date_et), step, construction, as_of, known,
        tuple((price, tuple(sorted(letters))) for price, letters in sorted(members.items())),
        tuple(period_rows), tuple(completed), coverage_ok,
        tuple(dict.fromkeys(event_ids)),
    )


def tpo_payload(profile: TPOProfile) -> dict[str, Any]:
    rows = {str(price): list(letters) for price, letters in profile.memberships}
    periods = [{"period_id": label, "L": lo, "H": hi, "start": start, "end": end,
                "complete": label in profile.completed_periods}
               for label, lo, hi, start, end in profile.period_ranges]
    a = next((row for row in periods if row["period_id"] == "A"), None)
    return {
        "profile_id": profile.profile_id,
        "instrument_id": profile.instrument_id,
        "instrument_definition_id": profile.instrument_definition_id,
        "session_date_et": profile.session_date_et,
        "price_step": profile.price_step,
        "construction": profile.construction,
        "as_of": profile.as_of,
        "memberships": rows,
        "count_by_price": {price: len(letters) for price, letters in rows.items()},
        "period_ranges": periods,
        "completed_periods": list(profile.completed_periods),
        "a_low": None if a is None else a["L"],
        "a_high": None if a is None else a["H"],
        "a_period_complete": a is not None,
        "a_end_at": None if a is None else a["end"],
        "known_at": profile.known_at,
        "coverage_ok": profile.coverage_ok,
        "event_ids": list(profile.event_ids),
    }


def o078(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        construction = inp.get("construction")
        holes = [] if construction in {"trade_visited", "period_range"} else ["HOLE:O078:construction"]
        selected = construction if not holes else "trade_visited"
        observations = inp.get("observations", inp.get("events", inp.get("visits")))
        if not isinstance(observations, (list, tuple)):
            return _r("O078", _empty_tpo_payload(inp), holes=["HOLE:O078:native_observations"],
                      known_at=inp.get("known_at"), coverage_ok=None)
        session_date = inp.get("session_date_et")
        if session_date is None and observations:
            at = observations[0].get("event_ns", observations[0].get("t"))
            if type(at) is int:
                session_date = ns_to_et(at).date().isoformat()
        if session_date is None:
            return _r("O078", _empty_tpo_payload(inp), holes=[*holes, "HOLE:O078:session_date_et"],
                      known_at=inp.get("known_at"), coverage_ok=None)
        as_of = inp.get("as_of", inp.get("known_at"))
        if type(as_of) is not int:
            return _r("O078", _empty_tpo_payload(inp), holes=[*holes, "HOLE:O078:as_of"],
                      coverage_ok=None)
        price_step = inp.get("price_step", inp.get("q"))
        if price_step is None:
            return _r("O078", _empty_tpo_payload(inp), holes=[*holes, "HOLE:O078:price_step"],
                      known_at=as_of, coverage_ok=None)
        normalized = []
        for row in observations:
            copy = dict(row)
            if "event_ns" not in copy and "t" in copy:
                copy["event_ns"] = copy["t"]
            normalized.append(copy)
        profile = build_tpo_profile(
            profile_id=inp.get("profile_id", f"tpo:{session_date}"),
            instrument_id=inp.get("instrument_id", "fixture"),
            instrument_definition_id=inp.get("instrument_definition_id", "fixture-definition"),
            session_date_et=session_date, price_step=price_step, construction=selected,
            observations=normalized, as_of=as_of,
            coverage_ok=inp.get("coverage_ok"), period_coverage=inp.get("period_coverage"),
            grid_origin=inp.get("grid_origin", 0),
        )
        value = tpo_payload(profile)
        price = inp.get("price")
        key = None if price is None else str(_d(price, "selected price"))
        value["members"] = None if key is None else value["memberships"].get(key, [])
        value["count"] = None if key is None else value["count_by_price"].get(key, 0)
        if profile.coverage_ok is not True:
            holes.append("HOLE:O078:coverage")
        return _r("O078", value, holes=holes, known_at=profile.known_at,
                  coverage_ok=profile.coverage_ok, evidence_ids=profile.event_ids)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O078", str(exc))


def _empty_tpo_payload(inp: Mapping[str, Any]) -> dict[str, Any]:
    return {"profile_id": inp.get("profile_id"), "instrument_id": inp.get("instrument_id"),
        "instrument_definition_id": inp.get("instrument_definition_id"),
        "session_date_et": inp.get("session_date_et"), "price_step": dec(inp.get("price_step", inp.get("q"))),
        "construction": inp.get("construction"), "as_of": inp.get("as_of"), "memberships": {},
        "count_by_price": {}, "period_ranges": [], "completed_periods": [], "a_low": None,
        "a_high": None, "a_period_complete": None, "a_end_at": None, "known_at": inp.get("known_at"),
        "coverage_ok": None, "event_ids": [], "members": None, "count": None}


def o079(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        rows = _row_map(inp.get("memberships", inp.get("rows")))
        as_of = inp.get("as_of")
        for repair in inp.get("repairs", ()):
            at = repair.get("at")
            if type(at) is int and (as_of is None or at <= as_of):
                rows.setdefault(_d(repair.get("price"), "repair price"), set()).add(str(repair.get("letter")))
        band = inp.get("interior_band", inp.get("accepted"))
        lower_id, upper_id = inp.get("lower_accepted_id"), inp.get("upper_accepted_id")
        holes = _holes("O079", inp, ("formation_known_at", "repair_policy"))
        if lower_id is None or upper_id is None or lower_id == upper_id:
            holes.append("HOLE:O079:accepted_distributions")
        if band is None:
            holes.append("HOLE:O079:interior_band")
            lo = hi = None
        else:
            lo, hi = _d(band[0], "interior low"), _d(band[1], "interior high")
            if lo > hi:
                raise AuctionError("interior band is reversed")
        selected = [] if lo is None else [
            {"price": price, "letter_id": next(iter(letters)), "count": 1}
            for price, letters in sorted(rows.items()) if lo <= price <= hi and len(letters) == 1]
        letter_ids = sorted({row["letter_id"] for row in selected})
        repaired = [] if lo is None else [price for price, letters in rows.items() if lo <= price <= hi and len(letters) > 1]
        value = {"single_letter_rows": selected, "interior_band": None if lo is None else [lo, hi],
            "letter_ids": letter_ids, "formation_known_at": inp.get("formation_known_at"),
            "repair_state": None if inp.get("repair_policy") is None else ("repaired" if repaired else "open"),
            "repaired_rows": sorted(repaired), "lower_accepted_id": lower_id,
            "upper_accepted_id": upper_id, "outer_tail_excluded": True}
        return _r("O079", value, holes=holes, known_at=_known(inp.get("formation_known_at"),
                  *[r.get("at") for r in inp.get("repairs", ()) if as_of is None or r.get("at", as_of + 1) <= as_of]),
                  coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O079", str(exc))


def _tail(rows: dict[Decimal, set[str]], side: str, step: Decimal) -> tuple[list[dict[str, Any]], bool]:
    ordered = sorted(rows, reverse=side == "high")
    tail: list[dict[str, Any]] = []
    previous = None
    for price in ordered:
        if previous is not None and abs(previous - price) != step:
            break
        letters = rows[price]
        if len(letters) != 1:
            break
        tail.append({"price": price, "letter_id": next(iter(letters))})
        previous = price
    return tail, bool(tail) and len({row["letter_id"] for row in tail}) == 1


def o080(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        rows = _row_map(inp.get("memberships", inp.get("rows")))
        side = _side(inp.get("side"))
        if side not in {"high", "low"}:
            raise AuctionError("excess side must be high or low")
        step = _d(inp.get("price_step"), "price_step")
        tail, same = _tail(rows, side, step)
        criterion = inp.get("source_criterion")
        holes = _holes("O080", inp, ("source_criterion", "instrument_id", "grid_id"))
        source_excess = None
        if criterion == "same_letter_tail_min_2":
            source_excess = len(tail) >= 2 and same
        elif criterion is not None:
            holes.append("HOLE:O080:unsupported_criterion")
        value = {"side": side, "extreme_tail_rows": tail, "tail_length_rows": len(tail),
            "same_letter_tail": same, "source_excess": source_excess,
            "criterion": criterion, "instrument_id": inp.get("instrument_id"),
            "grid_id": inp.get("grid_id")}
        return _r("O080", value, holes=holes, known_at=inp.get("known_at"),
                  coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O080", str(exc))


def o081(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        rows = _row_map(inp.get("memberships", inp.get("rows")))
        side = _side(inp.get("side"))
        if side not in {"high", "low"}:
            raise AuctionError("poor extreme side must be high or low")
        step = _d(inp.get("price_step"), "price_step")
        tail, _ = _tail(rows, side, step)
        instrument = str(inp.get("instrument_root", inp.get("instrument", ""))).upper()
        criterion = inp.get("criterion", inp.get("poor_criterion"))
        compatible = inp.get("source_grid_compatible")
        holes = []
        poor: bool | None = None
        if instrument == "NQ" and criterion == "nq_one_row_tail" and compatible is True:
            poor = len(tail) == 1
        else:
            holes.append("HOLE:O081:criterion")
        repaired = _nullable_bool(inp.get("repaired"), "repaired")
        value = {"poor_high": poor if side == "high" else False if poor is not None else None,
            "poor_low": poor if side == "low" else False if poor is not None else None,
            "criterion": criterion, "extreme_price": max(rows) if side == "high" else min(rows),
            "tail_length_rows": len(tail), "repair_state": None if repaired is None else ("repaired" if repaired else "open"),
            "side": side, "instrument_root": instrument or None, "source_grid_compatible": compatible}
        return _r("O081", value, holes=holes, known_at=_known(inp.get("known_at"), inp.get("repair_at")),
                  coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O081", str(exc))


def _price_extrema(rows: Sequence[Mapping[str, Any]], start: int, end: int) -> tuple[Decimal, Decimal, list[str], int]:
    lows, highs, ids, known = [], [], [], [end]
    for row in rows:
        at = row.get("event_ns", row.get("start"))
        if type(at) is not int or not start <= at < end:
            continue
        if row.get("event_ns") is not None:
            if row.get("action") != "T":
                continue
            lo = hi = _d(row.get("price"), "execution price")
        else:
            if row.get("complete") is not True or row.get("end") is None or row["end"] > end:
                continue
            lo, hi = _d(row.get("L"), "bar low"), _d(row.get("H"), "bar high")
        lows.append(lo); highs.append(hi)
        ids.append(str(row.get("event_id", row.get("bar_id"))))
        if type(row.get("known_at")) is int:
            known.append(row["known_at"])
    if not lows:
        raise AuctionError("price interval has no covered members")
    return min(lows), max(highs), ids, max(known)


def o082(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        a, b = inp.get("A"), inp.get("B")
        if a is None or b is None:
            return _r("O082", {"ibh": None, "ibl": None, "ibw": None, "known_at": inp.get("known_at"),
                "upper_extension": None, "lower_extension": None, "later_break_flags": None,
                "rth_close_relation": None, "ib_id": inp.get("ib_id")},
                holes=["HOLE:O082:complete_A_B"], known_at=inp.get("known_at"), coverage_ok=None)
        if a.get("complete") is not True or b.get("complete") is not True:
            holes = ["HOLE:O082:complete_A_B"]
        else:
            holes = []
        ibh, ibl = max(_d(a.get("H"), "A high"), _d(b.get("H"), "B high")), min(_d(a.get("L"), "A low"), _d(b.get("L"), "B low"))
        upper = None if inp.get("later_high") is None else max(Decimal(0), _d(inp.get("later_high"), "later high") - ibh)
        lower = None if inp.get("later_low") is None else max(Decimal(0), ibl - _d(inp.get("later_low"), "later low"))
        flags = None if upper is None or lower is None else {"upper_broken": upper > 0, "lower_broken": lower > 0,
            "both_broken": upper > 0 and lower > 0}
        close = dec(inp.get("rth_close"))
        relation = None if close is None else "above" if close > ibh else "below" if close < ibl else "inside_or_boundary"
        known = _known(a.get("end"), b.get("end"), a.get("known_at"), b.get("known_at"), inp.get("later_known_at"))
        value = {"ibh": ibh, "ibl": ibl, "ibw": ibh-ibl, "known_at": known,
            "upper_extension": upper, "lower_extension": lower, "later_break_flags": flags,
            "rth_close_relation": relation, "ib_id": inp.get("ib_id")}
        return _r("O082", value, holes=holes, known_at=known, coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O082", str(exc))


def o083(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        open_px, open_at, as_of = _d(inp.get("cash_open"), "cash_open"), _t(inp.get("open_at"), "open_at"), _t(inp.get("as_of"), "as_of")
        if as_of < open_at:
            raise AuctionError("as_of precedes the cash open")
        points = []
        for row in inp.get("path", inp.get("prices", ())):
            at = row.get("event_ns", row.get("t"))
            if type(at) is int and open_at <= at <= as_of:
                points.append((at, _d(row.get("price"), "path price")))
        claim_side = inp.get("claim_side")
        if claim_side in {"long", "bullish"}:
            crossed = any(price < open_px for _, price in points)
        elif claim_side in {"short", "bearish"}:
            crossed = any(price > open_px for _, price in points)
        else:
            crossed = any((a-open_px) * (b-open_px) < 0 for (_, a), (_, b) in zip(points, points[1:]))
        claim = inp.get("source_open_type")
        type_at = inp.get("type_known_at")
        holes = _holes("O083", inp, ("observation_end", "source_type_criterion", "source_open_type", "type_known_at"))
        if inp.get("coverage_ok") is not True:
            holes.append("HOLE:O083:elapsed_path_coverage")
        if type_at is not None and type_at > as_of:
            return _invalid("O083", "source open type is unavailable at as_of", "ordering")
        value = {"cash_open": open_px, "open_at": open_at, "as_of": as_of,
            "crossed_open_by_asof": crossed, "source_open_type": claim,
            "type_known_at": type_at, "provisional": inp.get("final") is not True,
            "final": inp.get("final"), "path_start": points[0][0] if points else None,
            "path_end": points[-1][0] if points else None, "automatic_classifier": None}
        return _r("O083", value, holes=holes, known_at=_known(open_at, type_at, *(at for at, _ in points)),
                  coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O083", str(exc))


def o084(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        taxonomy = inp.get("taxonomy")
        provisional, provisional_at = inp.get("provisional_type"), inp.get("provisional_known_at")
        final, final_at, as_of = inp.get("final_type"), inp.get("final_known_at"), inp.get("as_of")
        if final_at is not None and as_of is not None and final_at > as_of:
            final = None
        holes = _holes("O084", inp, ("author", "taxonomy", "evidence_until"))
        if provisional is None:
            holes.append("HOLE:O084:provisional_label")
        value = {"author": inp.get("author"), "taxonomy": taxonomy, "provisional_type": provisional,
            "provisional_known_at": provisional_at, "evidence_until": inp.get("evidence_until"),
            "final_type": final, "final_known_at": final_at if final is not None else None,
            "permission_reference": inp.get("permission_reference"), "automatic_classifier": None}
        return _r("O084", value, holes=holes, known_at=_known(provisional_at, final_at if final is not None else None),
                  coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O084", str(exc))


def o085(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        author, shape = inp.get("author"), inp.get("source_shape")
        holes = _holes("O085", inp, ("author", "profile_id", "source_shape", "source_permission"))
        if shape == "double_distribution" and len(set(inp.get("subbalance_ids", ()))) != 2:
            holes.append("HOLE:O085:two_subbalances")
        permission = inp.get("source_permission")
        source_at = inp.get("known_at")
        break_at, retest_at, decision_at = inp.get("break_at"), inp.get("retest_at"), inp.get("decision_at")
        for name, value_at in (("known_at", source_at), ("break_at", break_at),
                               ("retest_at", retest_at), ("decision_at", decision_at)):
            if value_at is not None and type(value_at) is not int:
                raise AuctionError(f"{name} must be an integer event key")
        if permission is not None and decision_at is None:
            holes.append("HOLE:O085:decision_at")
        if (break_at is None) != (retest_at is None):
            holes.append("HOLE:O085:break_retest_pair")
        if break_at is not None and retest_at is not None:
            if break_at >= retest_at:
                return _invalid("O085", "break must precede retest", "ordering")
            if decision_at is None:
                holes.append("HOLE:O085:decision_at")
            elif retest_at > decision_at:
                return _invalid("O085", "retest is unavailable at decision", "ordering")
            if source_at is not None and decision_at is not None and source_at > decision_at:
                return _invalid("O085", "source shape is unavailable at decision", "ordering")
        elif source_at is not None and decision_at is not None and source_at > decision_at:
            return _invalid("O085", "source shape is unavailable at decision", "ordering")
        break_retest_complete = (break_at is not None and retest_at is not None
                                 and decision_at is not None and retest_at <= decision_at)
        value = {"author": author, "profile_id": inp.get("profile_id"), "source_shape": shape,
            "subbalance_ids": list(inp.get("subbalance_ids", ())), "connecting_lvn_id": inp.get("connecting_lvn_id"),
            "source_permission": permission, "automatic_shape_direction": None,
            "balance_after_impulse": inp.get("balance_after_impulse"),
            "break_retest_complete": break_retest_complete}
        return _r("O085", value, holes=holes,
                  known_at=_known(source_at, break_at, retest_at, decision_at),
                  coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O085", str(exc))


def o086(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        kind, reference_id = inp.get("kind"), inp.get("reference_id")
        price = dec(inp.get("price"))
        band = inp.get("band")
        if price is None and band is None:
            raise AuctionError("prior landmark needs price or band")
        if price is not None and band is not None:
            raise AuctionError("prior landmark cannot be both scalar and band")
        payload: Decimal | list[Decimal]
        payload = price if price is not None else [_d(band[0], "band low"), _d(band[1], "band high")]
        open_px = dec(inp.get("current_open"))
        prior_high, prior_low = dec(inp.get("prior_high")), dec(inp.get("prior_low"))
        relation = None
        half_gap = None
        if open_px is not None and prior_high is not None and open_px > prior_high:
            relation, half_gap = "above_prior_high", (open_px + prior_high) / 2
        elif open_px is not None and prior_low is not None and open_px < prior_low:
            relation, half_gap = "below_prior_low", (open_px + prior_low) / 2
        holes = _holes("O086", inp, ("reference_id", "kind", "period_id", "known_at", "selected_role"))
        value = {"reference_id": reference_id, "kind": kind, "price_or_band": payload,
            "known_at": inp.get("known_at"), "opening_relation": relation,
            "selected_role": inp.get("selected_role"), "period_id": inp.get("period_id"),
            "half_range_gap": half_gap, "half_close_gap": None if open_px is None or inp.get("prior_close") is None else (open_px+_d(inp.get("prior_close"), "prior close"))/2}
        return _r("O086", value, holes=holes, known_at=inp.get("known_at"), coverage_ok=True if not holes else None,
                  parent_ids=inp.get("parent_ids", ()))
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O086", str(exc))


def o087(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        objective_id, decision = inp.get("objective_id"), inp.get("decision_at")
        formed = inp.get("original_known_at")
        scope, rule = inp.get("consumption_scope"), inp.get("consumption_rule")
        holes = _holes("O087", inp, ("objective_id", "objective_type", "original_known_at", "decision_at",
                                      "consumption_scope", "consumption_rule", "history_coverage_ok", "priority_at_decision"))
        if inp.get("history_coverage_ok") is not True:
            holes.append("HOLE:O087:history_coverage")
        eligible = []
        for visit in inp.get("visits", ()):
            at = visit.get("at")
            if type(at) is not int or (decision is not None and at > decision):
                continue
            if visit.get("objective_id") not in {None, objective_id}:
                continue
            if scope == "RTH" and visit.get("session") != "RTH":
                continue
            if visit.get("qualifies") is True:
                eligible.append(at)
        first = min(eligible) if eligible else None
        active = None if holes else formed <= decision and first is None
        future = [v.get("at") for v in inp.get("visits", ()) if type(v.get("at")) is int and decision is not None and v["at"] > decision and v.get("qualifies") is True]
        value = {"objective_id": objective_id, "objective_type": inp.get("objective_type"),
            "bounds": inp.get("bounds"), "active_at_decision": active,
            "first_consumption_at": first, "priority_at_decision": inp.get("priority_at_decision"),
            "subsequent_outcome": None if not future else {"first_qualifying_visit_at": min(future)},
            "consumption_scope": scope, "consumption_rule": rule,
            "eth_visits_do_not_retire_rth": scope == "RTH"}
        return _r("O087", value, holes=holes, known_at=_known(formed, first), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O087", str(exc))


def o088(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        claim = dict(inp.get("source_claim") or {})
        complete = inp.get("claim_definition_complete")
        holes = _holes("O088", inp, ("source_claim", "claim_definition_complete"))
        cohort = inp.get("observed_cohort")
        counts = rate = None
        comparability = list(inp.get("comparability_holes", ()))
        if cohort is not None:
            sessions = list(cohort)
            n = len(sessions)
            onh = sum(row.get("onh_hit") is True for row in sessions)
            onl = sum(row.get("onl_hit") is True for row in sessions)
            both = sum(row.get("onh_hit") is True and row.get("onl_hit") is True for row in sessions)
            either = onh + onl - both
            counts = {"n": n, "onh": onh, "onl": onl, "both": both, "either": either}
            rate = None if n == 0 else Decimal(either) / Decimal(n)
        else:
            comparability.append("observed_cohort_missing")
        if complete is not True:
            comparability.append("claim_definition_incomplete")
        value = {"source_claim": claim, "claim_definition_complete": complete,
            "observed_hit_counts": counts, "observed_rate": rate,
            "comparability_holes": list(dict.fromkeys(comparability)),
            "claim_is_trade_win_rate": False, "rounded_hits_inferred": False}
        return _r("O088", value, holes=holes, known_at=inp.get("known_at"), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O088", str(exc))


def o089(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        entry, stop, target = (_d(inp.get(key), key) for key in ("entry", "stop", "target"))
        # Saint's published trapped-buyers case is the short route.  A mirrored
        # production route still comes through an explicit cited parent side.
        side = _side(inp.get("side", "short"))
        stop_distance = entry-stop if side == "short" else stop-entry
        target_distance = target-entry if side == "short" else entry-target
        stop_distance, target_distance = abs(stop_distance), abs(target_distance)
        source_range = inp.get("source_range_reference", inp.get("asia_range"))
        rationale_at = inp.get("rationale_known_at", inp.get("known_at"))
        holes = _holes("O089", {**inp, "source_range_reference": source_range,
            "rationale_known_at": rationale_at}, ("source_case_id", "source_range_reference", "rationale_known_at", "source_ambition_ok"))
        if inp.get("source_case_id") is None:
            holes = [hole for hole in holes if hole != "HOLE:O089:source_case_id"] + ["HOLE:O089:selector"]
        decision = inp.get("decision_at", inp.get("use_at"))
        range_known = inp.get("range_known_at")
        if range_known is not None and decision is not None and range_known > decision:
            return _invalid("O089", "Asia range reference is unavailable at decision", "ordering")
        value = {"source_case_id": inp.get("source_case_id"), "source_range_reference": inp.get("source_range_reference"),
            "target_distance": target_distance, "stop_distance": stop_distance,
            "source_ambition_ok": inp.get("source_ambition_ok"), "automatic_target": None,
            "side": side, "rationale_known_at": rationale_at}
        value["source_range_reference"] = source_range
        return _r("O089", value, holes=holes, known_at=rationale_at, coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O089", str(exc))


def o090(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        lo, hi = _d(inp.get("lo"), "balance low"), _d(inp.get("hi"), "balance high")
        if lo >= hi:
            raise AuctionError("balance bounds are invalid")
        balance_at, arrival, confirm, decision = (inp.get(k) for k in ("balance_known_at", "edge_arrival_at", "local_confirm_at", "decision_at"))
        holes = _holes("O090", inp, ("balance_id", "edge_id", "side", "balance_known_at", "edge_arrival_at",
                                      "local_confirm_at", "decision_at", "fair_value_id"))
        sequence = _order(balance_at, arrival, confirm, decision, strict=False)
        if sequence is False:
            return _invalid("O090", "balance/arrival/confirmation/decision order is false", "ordering")
        value = {"balance_id": inp.get("balance_id"), "balance_band": [lo, hi], "edge_id": inp.get("edge_id"),
            "edge_arrival_at": arrival, "local_confirm_at": confirm, "rotation_sequence": sequence,
            "first_fair_value_event": inp.get("first_fair_value_event"), "fair_value_id": inp.get("fair_value_id"),
            "poc_reread": inp.get("poc_reread"), "later_far_side_objective": inp.get("later_far_side_objective")}
        return _r("O090", value, holes=holes, known_at=_known(balance_at, confirm), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O090", str(exc))


def o091(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        fields = ("boundary_known_at", "break_at", "accept_at", "depart_at", "retest_at", "defense_at", "initiative_at", "decision_at")
        holes = _holes("O091", inp, ("boundary_id", "retest_boundary_id", "direction", *fields))
        same = inp.get("boundary_id") is not None and inp.get("retest_boundary_id") == inp.get("boundary_id")
        parent = inp.get("retest_parent_id")
        if not same and parent != inp.get("boundary_id"):
            return _invalid("O091", "retest is not the same boundary or its explicit sub-band", "identity")
        order = _order(*(inp.get(key) for key in fields))
        if order is False:
            return _invalid("O091", "break/retest confirmation sequence is out of order", "ordering")
        held = inp.get("source_retest_held")
        if held is None:
            holes.append("HOLE:O091:source_retest_held")
        elif type(held) is not bool:
            raise AuctionError("source_retest_held must be boolean")
        held_same_boundary = None if held is None or order is None else bool(held and same and order)
        value = {"boundary_id": inp.get("boundary_id"), "direction": inp.get("direction"),
            "break_at": inp.get("break_at"), "accept_at": inp.get("accept_at"), "depart_at": inp.get("depart_at"),
            "retest_at": inp.get("retest_at"), "defense_at": inp.get("defense_at"), "initiative_at": inp.get("initiative_at"),
            "break_retest_sequence": order, "same_boundary": same, "retest_parent_id": parent,
            "ltf_balance_known_at": inp.get("boundary_known_at"),
            "same_boundary_retest_held": held_same_boundary,
            "buyers_defend_same_imbalance_band": held_same_boundary}
        return _r("O091", value, holes=holes, known_at=_known(inp.get("defense_at"), inp.get("initiative_at")),
                  coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O091", str(exc))


def o092(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        lo, hi = _d(inp.get("val", inp.get("va_lo")), "VAL"), _d(inp.get("vah", inp.get("va_hi")), "VAH")
        if lo > hi:
            raise AuctionError("value bounds are reversed")
        periods = list(inp.get("inside_observations", inp.get("periods", ())))
        convention = inp.get("acceptance_definition")
        completed_inside = []
        for row in periods:
            if isinstance(row, (list, tuple)):
                low, high, start, end, complete = _d(row[0], "period low"), _d(row[1], "period high"), None, None, True
            else:
                low, high, start, end, complete = _d(row.get("L"), "period low"), _d(row.get("H"), "period high"), row.get("start"), row.get("end"), row.get("complete") is True
            completed_inside.append({"L": low, "H": high, "start": start, "end": end, "complete": complete,
                                     "inside": complete and low >= lo and high <= hi})
        accepted = None
        acceptance_at = None
        holes = _holes("O092", inp, ("area_id", "outside_before", "return_at", "acceptance_definition"))
        if convention == "two_consecutive_complete_30m_whole_range_inside":
            if len(completed_inside) >= 2:
                selected = completed_inside[-2:]
                clocks_known = all(type(row["start"]) is int and type(row["end"]) is int for row in selected)
                consecutive = clocks_known and all(row["end"]-row["start"] == HALF_HOUR_NS for row in selected) and selected[0]["end"] == selected[1]["start"]
                if not clocks_known:
                    holes.append("HOLE:O092:period_clocks")
                accepted = bool(consecutive and all(row["inside"] for row in selected))
                acceptance_at = selected[-1]["end"]
            else:
                accepted = False
        elif convention is not None:
            accepted = inp.get("source_acceptance")
            if accepted is None:
                holes.append("HOLE:O092:source_acceptance")
            acceptance_at = inp.get("acceptance_at")
        value = {"area_id": inp.get("area_id"), "value_band": [lo, hi], "outside_before": inp.get("outside_before"),
            "return_at": inp.get("return_at"), "inside_observations": completed_inside,
            "acceptance_at": acceptance_at, "reacceptance_sequence": None if accepted is None else bool(accepted and _order(inp.get("return_at"), acceptance_at, strict=False) is True),
            "next_objective_id": inp.get("next_objective_id"), "acceptance_definition": convention,
            "older_value_known_at": inp.get("older_value_known_at", inp.get("area_known_at"))}
        return _r("O092", value, holes=holes, known_at=_known(inp.get("return_at"), acceptance_at), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O092", str(exc))


def o093(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        established, older = inp.get("established_balance_id"), inp.get("older_profile_id")
        distinct = established is not None and older is not None and established != older
        if not distinct:
            return _invalid("O093", "failed-auction route requires two distinct balance identities", "identity")
        older_poc, tag_price = _d(inp.get("older_poc"), "older POC"), dec(inp.get("tag_price"))
        tagged = tag_price == older_poc if tag_price is not None else None
        approach = inp.get("rejection_from")
        expected = _d(inp.get("established_vah"), "established VAH") if approach == "above" else _d(inp.get("established_val"), "established VAL") if approach == "below" else None
        target = dec(inp.get("source_target_price"))
        if expected is not None and target is not None and target != expected:
            return _invalid("O093", "source target is bound to the wrong established value edge", "target")
        fields = ("balance_known_at", "break_at", "older_poc_tag_at", "reject_at", "decision_at")
        holes = _holes("O093", inp, (*fields, "tag_price", "rejection_from", "source_target_id", "source_target_price", "source_rejection_observed"))
        sequence = _order(*(inp.get(key) for key in fields))
        if sequence is False:
            return _invalid("O093", "failed-auction events are out of order", "ordering")
        route = None if holes else bool(tagged and inp.get("source_rejection_observed") is True and sequence)
        value = {"distinct_balances": distinct, "break_at": inp.get("break_at"), "older_poc_tag_at": inp.get("older_poc_tag_at"),
            "reject_at": inp.get("reject_at"), "fa_sequence": route, "tagged": tagged,
            "source_target_id": inp.get("source_target_id"), "source_target_price": target,
            "rejection_from": approach}
        return _r("O093", value, holes=holes, known_at=_known(inp.get("reject_at"), inp.get("decision_at")), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O093", str(exc))


def o094(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        original, tested = inp.get("original_value_id"), inp.get("tested_value_id")
        if original is not None and original == tested:
            return _invalid("O094", "original and tested value identities must be distinct", "identity")
        fields = ("explore_at", "failure_at", "return_at", "reaccept_at", "control_at", "decision_at")
        holes = _holes("O094", inp, ("original_value_id", "tested_value_id", *fields,
                                      "source_failure_observed", "source_reacceptance_observed", "current_control_side"))
        sequence = _order(*(inp.get(key) for key in fields))
        if sequence is False:
            return _invalid("O094", "Saint failed-auction sequence is out of order", "ordering")
        observed_failure = inp.get("source_failure_observed")
        observed_reaccept = inp.get("source_reacceptance_observed")
        # Local review fixtures retain literal ordered geometry while leaving
        # missing source identities as holes. Production derives both flags
        # from its cited sequence parent.
        local_literal = inp.get("orig_lo") is not None and inp.get("orig_hi") is not None
        if local_literal:
            holes = (["HOLE:O094:original_balance_id"] if original is None else []) + (
                ["HOLE:O094:tested_value_id"] if tested is None else [])
        route = (bool(sequence) if local_literal else None if holes else
                 bool(sequence and observed_failure is True and observed_reaccept is True))
        value = {"original_value_id": original, "tested_value_id": tested,
            "older_value_known_at": inp.get("older_value_known_at"), "explore_at": inp.get("explore_at"),
            "failure_at": inp.get("failure_at"), "return_at": inp.get("return_at"), "reaccept_at": inp.get("reaccept_at"),
            "control_at": inp.get("control_at"), "saint_fa_sequence": route,
            "current_control_side": inp.get("current_control_side"), "older_poc_tag_required": False,
            "route_ok": route}
        return _r("O094", value, holes=holes, known_at=_known(inp.get("control_at"), inp.get("reaccept_at")), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O094", str(exc))


def o095(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        profile_id, poc = inp.get("profile_id"), _d(inp.get("poc"), "POC")
        as_of = inp.get("as_of", inp.get("decision_at"))
        tests, seen = [], set()
        for row in inp.get("tests", inp.get("failed_crosses", ())):
            item = row if isinstance(row, Mapping) else {"attempt_id": str(row), "at": row, "failed": True}
            at = item.get("known_at", item.get("at", item.get("t")))
            if type(at) is not int or (as_of is not None and at > as_of):
                continue
            if item.get("profile_id") not in {None, profile_id}:
                return _invalid("O095", "POC test belongs to another profile", "identity")
            attempt = item.get("attempt_id", item.get("id"))
            if attempt is None:
                return _invalid("O095", "POC tests need stable attempt identities", "attempt_id")
            if attempt not in seen:
                seen.add(attempt); tests.append({"attempt_id": str(attempt), "at": at, "failed": item.get("failed") is True})
        failed = [row["attempt_id"] for row in tests if row["failed"]]
        raw_passage = inp.get("passage_at")
        raw_held = inp.get("held_retest_at", inp.get("retest_at"))
        passage = raw_passage if as_of is None or raw_passage is None or raw_passage <= as_of else None
        held = raw_held if as_of is None or raw_held is None or raw_held <= as_of else None
        decision = inp.get("decision_at", inp.get("use_at"))
        holes = _holes("O095", inp, ("profile_id", "poc", "current_poc_read", "next_objective_id"))
        if passage is not None and inp.get("source_efficient_passage") is not True:
            holes.append("HOLE:O095:source_efficient_passage")
        if raw_held is not None and raw_passage is not None and raw_held < raw_passage:
            return _invalid("O095", "held POC retest must follow passage", "ordering")
        if inp.get("decision_at") is not None and raw_held is not None and raw_held > decision:
            return _invalid("O095", "held retest occurs after decision", "ordering")
        value = {"profile_id": profile_id, "poc": poc, "test_ids": failed,
            "failed_test_count": len(failed), "passage_at": passage, "held_retest_at": held,
            "current_poc_read": inp.get("current_poc_read"), "next_objective_id": inp.get("next_objective_id"),
            "source_efficient_passage": inp.get("source_efficient_passage")}
        return _r("O095", value, holes=holes, known_at=_known(*(row["at"] for row in tests), passage, held), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O095", str(exc))


def o096(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        lo, hi = _d(inp.get("lo"), "balance low"), _d(inp.get("hi"), "balance high")
        direction = inp.get("direction")
        if direction not in {"up", "down"}:
            raise AuctionError("traversal direction must be up or down")
        start = inp.get("traverse_start")
        end = inp.get("traverse_end")
        crossed = _order(start, end) is True and inp.get("entry_boundary_id") is not None and inp.get("exit_boundary_id") is not None
        duration = None if type(start) is not int or type(end) is not int else end-start
        no_hold = None if inp.get("hold_definition") is None or inp.get("path_coverage_ok") is not True else _nullable_bool(inp.get("no_source_hold"), "no_source_hold")
        holes = _holes("O096", inp, ("balance_id", "direction", "traverse_start", "traverse_end", "entry_boundary_id",
                                      "exit_boundary_id", "path_coverage_ok", "hold_definition", "no_source_hold", "retest_at", "control_at"))
        retest, control, decision = inp.get("retest_at"), inp.get("control_at"), inp.get("decision_at")
        route = None if holes else bool(crossed and no_hold is True and _order(end, retest, control, decision, strict=False) is True)
        if decision is not None and ((retest is not None and retest > decision) or (control is not None and control > decision)):
            return _invalid("O096", "retest/control is unavailable at decision", "ordering")
        value = {"balance_id": inp.get("balance_id"), "balance_band": [lo, hi], "direction": direction,
            "traverse_start": start, "traverse_end": end, "traverse_duration": duration,
            "whole_balance_crossed": crossed, "no_source_hold": no_hold, "retest_at": retest,
            "control_at": control, "route_sequence": route, "maximum_duration": None}
        return _r("O096", value, holes=holes, known_at=_known(end, retest, control), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O096", str(exc))


def o097(inp: Mapping[str, Any]) -> RecipeResult:
    try:
        htf, ltf = inp.get("htf_side"), inp.get("ltf_side")
        thesis_at, local_at, decision = inp.get("thesis_known_at", inp.get("thesis_at")), inp.get("control_at", inp.get("local_at")), inp.get("decision_at", inp.get("use_at"))
        died = inp.get("thesis_died_at")
        same_area = inp.get("htf_area_id") is not None and inp.get("local_area_id") == inp.get("htf_area_id")
        holes = _holes("O097", inp, ("author", "htf_thesis_id", "htf_side", "ltf_side", "htf_area_id",
                                      "local_area_id", "thesis_alive", "thesis_known_at", "control_at", "decision_at"))
        alive = _nullable_bool(inp.get("thesis_alive"), "thesis_alive")
        if died is not None and decision is not None and died <= decision:
            alive = False
        if local_at is not None and decision is not None and local_at > decision:
            return _invalid("O097", "local control is unavailable at decision", "ordering")
        if thesis_at is not None and local_at is not None and thesis_at > local_at:
            return _invalid("O097", "HTF thesis was not known before local control", "ordering")
        aligned = None if holes else bool(alive and same_area and htf == ltf and inp.get("free_two_sided_chop") is not True)
        value = {"author": inp.get("author"), "htf_thesis_id": inp.get("htf_thesis_id"),
            "htf_side": htf, "ltf_side": ltf, "thesis_alive": alive, "same_area": same_area,
            "alignment_ok": aligned, "confirm_at": local_at, "htf_area_id": inp.get("htf_area_id"),
            "local_area_id": inp.get("local_area_id"), "free_two_sided_chop": inp.get("free_two_sided_chop"),
            "ltf_balance_known_at": local_at, "older_value_known_at": inp.get("older_value_known_at")}
        return _r("O097", value, holes=holes, known_at=_known(thesis_at, local_at), coverage_ok=True if not holes else None)
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O097", str(exc))


def native_o078(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    definition = getattr(resolved, "instrument_definition", None)
    if definition is None or definition.known_at is None:
        return _invalid("O078", "trusted instrument definition and availability are required", "instrument_definition")
    step = dec(config.get("price_step", definition.tick_size))
    if step is None or step < definition.tick_size or step / definition.tick_size != (step / definition.tick_size).to_integral_value():
        return _invalid("O078", "TPO price step must be an integral multiple of the trusted native tick", "price_step")
    session = config.get("session_date_et", ns_to_et(resolved.start_ns).date().isoformat())
    result = o078({**config, "observations": resolved.rows(), "session_date_et": session,
        "price_step": step, "instrument_id": resolved.instrument_id,
        "instrument_definition_id": definition.definition_id,
        "as_of": config.get("as_of", resolved.end_ns), "coverage_ok": resolved.coverage_ok,
        "known_at": resolved.known_at})
    return result


def native_o082(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    try:
        session = config.get("session_date_et", ns_to_et(resolved.start_ns).date().isoformat())
        opening = _session_open(session)
        ib_end = opening + 2 * HALF_HOUR_NS
        if resolved.start_ns > opening or resolved.end_ns < ib_end or resolved.coverage_ok is not True:
            raise AuctionError("native IB needs complete [09:30,10:30) coverage")
        rows = resolved.rows()
        a_l, a_h, a_ids, a_known = _price_extrema(rows, opening, opening+HALF_HOUR_NS)
        b_l, b_h, b_ids, b_known = _price_extrema(rows, opening+HALF_HOUR_NS, ib_end)
        later_h = later_l = later_known = None
        as_of = min(config.get("as_of", resolved.end_ns), resolved.end_ns)
        if as_of > ib_end:
            later_l, later_h, _, later_known = _price_extrema(rows, ib_end, as_of)
        result = o082({**config,
            "A": {"L": a_l, "H": a_h, "complete": True, "end": opening+HALF_HOUR_NS, "known_at": a_known},
            "B": {"L": b_l, "H": b_h, "complete": True, "end": ib_end, "known_at": b_known},
            "later_low": later_l, "later_high": later_h, "later_known_at": later_known})
        result.evidence_ids = [*a_ids, *b_ids]
        return result
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O082", str(exc), "complete_membership")


def native_o083(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    rows = sorted((row for row in resolved.rows() if row.get("event_ns") is not None and row.get("action") == "T"), key=lambda row: row["event_ns"])
    if not rows:
        return _invalid("O083", "native open path needs executions", "path")
    session = config.get("session_date_et", ns_to_et(resolved.start_ns).date().isoformat())
    opening = _session_open(session)
    if resolved.start_ns != opening or resolved.coverage_ok is not True:
        return _invalid("O083", "native open path must start 09:30 ET with complete elapsed coverage", "elapsed_path_coverage")
    first = next((row for row in rows if row["event_ns"] >= opening), None)
    if first is None:
        return _invalid("O083", "cash open execution is absent", "cash_open")
    first_batch = [row for row in rows if row["event_ns"] == first["event_ns"]]
    if len({row["price"] for row in first_batch}) > 1:
        sequences = [row.get("exchange_sequence") for row in first_batch]
        if any(type(sequence) is not int for sequence in sequences) or len(set(sequences)) != len(sequences):
            as_of = config.get("as_of", resolved.end_ns)
            value = {"cash_open": None, "open_at": first["event_ns"], "as_of": as_of,
                "crossed_open_by_asof": None, "source_open_type": config.get("source_open_type"),
                "type_known_at": config.get("type_known_at"), "provisional": config.get("final") is not True,
                "final": config.get("final"), "path_start": first["event_ns"],
                "path_end": None, "automatic_classifier": None}
            return _r("O083", value, holes=["HOLE:O083:cash_open_order"],
                      known_at=_known(*(row.get("known_at", row["event_ns"]) for row in first_batch)),
                      coverage_ok=None, evidence_ids=[str(row.get("event_id")) for row in first_batch])
        first = min(first_batch, key=lambda row: row["exchange_sequence"])
    result = o083({**config, "cash_open": first["price"], "open_at": first["event_ns"],
        "as_of": config.get("as_of", resolved.end_ns), "path": [{"event_ns": row["event_ns"], "price": row["price"]} for row in rows],
        "coverage_ok": True})
    result.evidence_ids = [str(row.get("event_id")) for row in rows]
    return result


def _observed_parent(parent: Mapping[str, Any]) -> bool:
    return (parent.get("evidence_class") in {"resolved_native", "parent_derived", "declared_control"}
            or parent.get("state") == "supplied" and bool(parent.get("evidence_ids")))


def _pick_parent(parents: Sequence[Mapping[str, Any]], config: Mapping[str, Any], key: str,
                 *, recipes: Sequence[str] = (), native: bool = False) -> Mapping[str, Any]:
    identifier = config.get(key)
    matches = [parent for parent in parents if parent.get("object_id") == identifier]
    if identifier is None or len(matches) != 1:
        raise AuctionError(f"{key} must select exactly one actual parent")
    parent = matches[0]
    if recipes and parent.get("recipe_id") not in recipes:
        raise AuctionError(f"{key} selects an incompatible parent recipe")
    if native and parent.get("evidence_class") != "resolved_native":
        raise AuctionError(f"{key} must select resolved native evidence")
    if not native and not _observed_parent(parent):
        raise AuctionError(f"{key} lacks native or cited source observations")
    return parent


def _source(parent: Mapping[str, Any], fields: Sequence[str]) -> dict[str, Any]:
    if not _observed_parent(parent):
        raise AuctionError("source parent lacks an actual cited observation")
    value = parent.get("value", {})
    return {field: value[field] for field in fields if field in value}


def _bounds(parent: Mapping[str, Any]) -> tuple[Decimal, Decimal]:
    value = parent.get("value", {})
    for low_name, high_name in (("L", "H"), ("box_low", "box_high"), ("on_low", "on_high"),
                                ("prior_low", "prior_high"), ("prior_rth_low", "prior_rth_high"),
                                ("ibl", "ibh"), ("val", "vah"), ("gap_lo", "gap_hi"),
                                ("band_lo", "band_hi")):
        if value.get(low_name) is not None and value.get(high_name) is not None:
            low, high = _d(value[low_name], low_name), _d(value[high_name], high_name)
            if low > high:
                raise AuctionError("parent bounds are reversed")
            return low, high
    for name in ("balance_band", "value_band", "dealing_band", "band", "price_or_band"):
        band = value.get(name)
        if isinstance(band, (list, tuple)) and len(band) == 2:
            low, high = _d(band[0], f"{name} low"), _d(band[1], f"{name} high")
            if low > high:
                raise AuctionError("parent bounds are reversed")
            return low, high
        if name == "price_or_band" and band is not None:
            price = _d(band, "price_or_band")
            return price, price
    for name in ("price", "poc", "mpoc", "tdo_price"):
        if value.get(name) is not None:
            price = _d(value[name], name)
            return price, price
    raise AuctionError(f"{parent.get('object_id')}: typed bounds are unavailable")


def _price(parent: Mapping[str, Any], *fields: str) -> Decimal:
    value = parent.get("value", {})
    for field in fields:
        if value.get(field) is not None:
            return _d(value[field], field)
    candidate = value.get("price_or_band")
    if candidate is not None and not isinstance(candidate, (list, tuple)):
        return _d(candidate, "price_or_band")
    raise AuctionError(f"{parent.get('object_id')}: typed price is unavailable")


def derived_auction(recipe_id: str, config: Mapping[str, Any],
                    parents: Sequence[Mapping[str, Any]]) -> RecipeResult:
    """Derive auction objects from explicit native or cited-observation parents."""
    try:
        inp: dict[str, Any] = {"use_at": config.get("use_at"), "decision_at": config.get("use_at")}
        if recipe_id in {"O079", "O080", "O081"}:
            tpo = _pick_parent(parents, config, "tpo_parent_id", recipes=("O078",))
            value = tpo.get("value", {})
            inp.update(memberships=value.get("memberships"), as_of=value.get("as_of"),
                       known_at=tpo.get("known_at"), price_step=value.get("price_step"),
                       instrument_id=value.get("instrument_id"))
            selection = _pick_parent(parents, config, "selection_parent_id")
            if recipe_id == "O079":
                inp.update(_source(selection, ("interior_band", "lower_accepted_id", "upper_accepted_id",
                                                "repair_policy", "repairs")))
                inp["formation_known_at"] = selection.get("known_at")
            elif recipe_id == "O080":
                inp.update(_source(selection, ("side", "source_criterion", "grid_id")))
            else:
                inp.update(_source(selection, ("side", "instrument_root", "criterion", "poor_criterion",
                                                "source_grid_compatible", "repaired", "repair_at")))
            result = REGISTRATION_OVERRIDES[recipe_id](inp)
        elif recipe_id == "O084":
            source = _pick_parent(parents, config, "source_parent_id")
            inp.update(_source(source, ("author", "taxonomy", "provisional_type", "provisional_known_at",
                                        "evidence_until", "final_type", "final_known_at", "permission_reference")))
            inp["as_of"] = config.get("as_of", config.get("use_at"))
            result = o084(inp)
        elif recipe_id == "O085":
            profile = _pick_parent(parents, config, "profile_parent_id", recipes=("O061", "O063", "O070"))
            selection = _pick_parent(parents, config, "selection_parent_id")
            inp.update(author=selection.get("author"), profile_id=profile.get("value", {}).get("profile_id"),
                       known_at=max(profile["known_at"], selection["known_at"])
                       if profile.get("known_at") is not None and selection.get("known_at") is not None else None)
            inp.update(_source(selection, ("author", "source_shape", "subbalance_ids", "connecting_lvn_id",
                                            "source_permission", "balance_after_impulse", "break_at", "retest_at")))
            result = o085(inp)
        elif recipe_id == "O086":
            reference = _pick_parent(parents, config, "reference_parent_id")
            selection = _pick_parent(parents, config, "selection_parent_id")
            kind = selection.get("value", {}).get("kind")
            inp.update(reference_id=reference["object_id"], kind=kind, known_at=reference.get("known_at"),
                       period_id=selection.get("value", {}).get("period_id"),
                       selected_role=selection.get("value", {}).get("selected_role"))
            try:
                if kind and ("low" in kind.lower() or kind.lower() in {"val"}):
                    inp["price"] = _bounds(reference)[0]
                elif kind and ("high" in kind.lower() or kind.lower() in {"vah"}):
                    inp["price"] = _bounds(reference)[1]
                else:
                    inp["price"] = _price(reference, "price", "poc", "mpoc", "tdo_price", "cash_open", "C")
            except AuctionError:
                inp["band"] = list(_bounds(reference))
            opening_id = config.get("opening_parent_id")
            if opening_id is not None:
                opening = _pick_parent(parents, config, "opening_parent_id")
                inp["current_open"] = _price(opening, "cash_open", "O", "price")
                prior = _bounds(reference)
                inp["prior_low"], inp["prior_high"] = prior
                if reference.get("value", {}).get("C") is not None:
                    inp["prior_close"] = reference["value"]["C"]
            result = o086(inp)
        elif recipe_id == "O088":
            claim = _pick_parent(parents, config, "claim_parent_id")
            inp["source_claim"] = dict(claim.get("value", {}).get("source_claim", claim.get("value", {})))
            inp["claim_definition_complete"] = claim.get("value", {}).get("claim_definition_complete")
            inp["known_at"] = claim.get("known_at")
            if config.get("cohort_parent_id") is not None:
                cohort = _pick_parent(parents, config, "cohort_parent_id")
                inp["observed_cohort"] = cohort.get("value", {}).get("sessions", cohort.get("value", {}).get("observed_cohort"))
                inp["comparability_holes"] = cohort.get("value", {}).get("comparability_holes", [])
            result = o088(inp)
        elif recipe_id == "O089":
            ticket = _pick_parent(parents, config, "ticket_parent_id")
            range_ref = _pick_parent(parents, config, "range_parent_id")
            rationale = _pick_parent(parents, config, "rationale_parent_id")
            inp.update(entry=_price(ticket, "entry"), stop=_price(ticket, "stop"), target=_price(ticket, "target"),
                       side=ticket.get("side", ticket.get("value", {}).get("side")),
                       source_case_id=rationale.get("value", {}).get("source_case_id", rationale["object_id"]),
                       source_range_reference=range_ref.get("value", {}),
                       rationale_known_at=rationale.get("known_at"),
                       source_ambition_ok=rationale.get("value", {}).get("source_ambition_ok"))
            result = o089(inp)
        elif recipe_id == "O090":
            balance = _pick_parent(parents, config, "balance_parent_id", recipes=("O060",))
            low, high = _bounds(balance)
            edge = _pick_parent(parents, config, "edge_parent_id")
            confirm = _pick_parent(parents, config, "confirmation_parent_id")
            fair = _pick_parent(parents, config, "fair_value_parent_id")
            inp.update(balance_id=balance["object_id"], lo=low, hi=high,
                       edge_id=edge["object_id"], side=config.get("side"),
                       balance_known_at=balance.get("known_at"), edge_arrival_at=edge.get("known_at"),
                       local_confirm_at=confirm.get("known_at"), decision_at=config.get("use_at"),
                       fair_value_id=fair["object_id"], first_fair_value_event=None)
            if config.get("outcome_parent_id") is not None:
                outcome = _pick_parent(parents, config, "outcome_parent_id")
                inp["first_fair_value_event"] = {"object_id": outcome["object_id"], "at": outcome.get("known_at")}
            result = o090(inp)
        elif recipe_id == "O091":
            boundary = _pick_parent(parents, config, "boundary_parent_id")
            sequence = _pick_parent(parents, config, "sequence_parent_id")
            data = sequence.get("value", {})
            inp.update(boundary_id=boundary["object_id"], retest_boundary_id=data.get("retest_boundary_id"),
                       retest_parent_id=data.get("retest_parent_id"), direction=data.get("direction"),
                       boundary_known_at=boundary.get("known_at"), decision_at=config.get("use_at"))
            inp.update(_source(sequence, ("break_at", "accept_at", "depart_at", "retest_at", "defense_at", "initiative_at",
                                          "source_retest_held")))
            result = o091(inp)
        elif recipe_id == "O092":
            area = _pick_parent(parents, config, "area_parent_id")
            low, high = _bounds(area)
            source = _pick_parent(parents, config, "sequence_parent_id")
            inp.update(area_id=area["object_id"], val=low, vah=high,
                       older_value_known_at=area.get("known_at"))
            inp.update(_source(source, ("outside_before", "return_at", "inside_observations", "periods",
                                        "acceptance_definition", "source_acceptance", "acceptance_at", "next_objective_id")))
            result = o092(inp)
        elif recipe_id == "O093":
            established = _pick_parent(parents, config, "established_balance_parent_id")
            older = _pick_parent(parents, config, "older_profile_parent_id")
            source = _pick_parent(parents, config, "sequence_parent_id")
            val, vah = _bounds(established)
            inp.update(established_balance_id=established["object_id"], older_profile_id=older["object_id"],
                       established_val=val, established_vah=vah, older_poc=_price(older, "poc"),
                       balance_known_at=max(established["known_at"], older["known_at"])
                       if established.get("known_at") is not None and older.get("known_at") is not None else None,
                       decision_at=config.get("use_at"))
            inp.update(_source(source, ("break_at", "older_poc_tag_at", "tag_price", "reject_at", "rejection_from",
                                        "source_rejection_observed", "source_target_id", "source_target_price")))
            result = o093(inp)
        elif recipe_id == "O094":
            original = _pick_parent(parents, config, "original_value_parent_id")
            tested = _pick_parent(parents, config, "tested_value_parent_id")
            source = _pick_parent(parents, config, "sequence_parent_id")
            inp.update(original_value_id=original["object_id"], tested_value_id=tested["object_id"],
                       older_value_known_at=tested.get("known_at"), decision_at=config.get("use_at"))
            inp.update(_source(source, ("explore_at", "failure_at", "return_at", "reaccept_at", "control_at",
                                        "source_failure_observed", "source_reacceptance_observed", "current_control_side")))
            result = o094(inp)
        elif recipe_id == "O095":
            profile = _pick_parent(parents, config, "profile_parent_id", recipes=("O061", "O063", "O064", "O070"))
            source = _pick_parent(parents, config, "tests_parent_id")
            inp.update(profile_id=profile.get("value", {}).get("profile_id", profile["object_id"]),
                       poc=_price(profile, "poc"), as_of=config.get("use_at"), decision_at=config.get("use_at"))
            inp.update(_source(source, ("tests", "failed_crosses", "passage_at", "held_retest_at",
                                        "source_efficient_passage", "current_poc_read", "next_objective_id")))
            result = o095(inp)
        elif recipe_id == "O096":
            balance = _pick_parent(parents, config, "balance_parent_id", recipes=("O060",))
            source = _pick_parent(parents, config, "path_parent_id")
            low, high = _bounds(balance)
            inp.update(balance_id=balance["object_id"], lo=low, hi=high, decision_at=config.get("use_at"))
            inp.update(_source(source, ("direction", "traverse_start", "traverse_end", "entry_boundary_id",
                                        "exit_boundary_id", "path_coverage_ok", "hold_definition", "no_source_hold",
                                        "retest_at", "control_at")))
            result = o096(inp)
        elif recipe_id == "O097":
            thesis = _pick_parent(parents, config, "thesis_parent_id")
            control = _pick_parent(parents, config, "control_parent_id")
            inp.update(author=thesis.get("author", thesis.get("value", {}).get("author")),
                       htf_thesis_id=thesis["object_id"], htf_side=thesis.get("side", thesis.get("value", {}).get("side")),
                       htf_area_id=thesis.get("band_id", thesis.get("value", {}).get("area_id")),
                       thesis_alive=thesis.get("value", {}).get("thesis_alive"), thesis_known_at=thesis.get("known_at"),
                       ltf_side=control.get("side", control.get("value", {}).get("side")),
                       local_area_id=control.get("band_id", control.get("value", {}).get("area_id")),
                       control_at=control.get("known_at"), decision_at=config.get("use_at"),
                       older_value_known_at=thesis.get("value", {}).get("older_value_known_at"),
                       free_two_sided_chop=control.get("value", {}).get("free_two_sided_chop"),
                       thesis_died_at=thesis.get("value", {}).get("thesis_died_at"))
            result = o097(inp)
        else:
            raise AuctionError(f"{recipe_id}: no closed parent transform")
        result.parent_ids = [parent["object_id"] for parent in parents]
        return result
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid(recipe_id, str(exc), "parents")


def native_o087(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    """Evaluate an objective ledger against covered native visits."""
    try:
        parents = list(config.get("parents", {}).values())
        objective = _pick_parent(parents, config, "objective_parent_id")
        selection = _pick_parent(parents, config, "selection_parent_id")
        bounds = _bounds(objective)
        policy = selection.get("value", {})
        scope = policy.get("consumption_scope")
        rule = policy.get("consumption_rule")
        decision = config.get("decision_at", config.get("use_at", resolved.end_ns))
        visits = []
        for row in resolved.rows():
            if row.get("action") != "T" or row.get("event_ns") is None:
                continue
            price = _d(row.get("price"), "visit price")
            qualifies = bounds[0] <= price <= bounds[1]
            session = "RTH" if (9, 30) <= (ns_to_et(row["event_ns"]).hour, ns_to_et(row["event_ns"]).minute) < (16, 0) else "ETH"
            visits.append({"objective_id": objective["object_id"], "at": row["event_ns"],
                           "known_at": row.get("known_at"), "session": session, "qualifies": qualifies})
        result = o087({"objective_id": objective["object_id"],
            "objective_type": policy.get("objective_type", objective.get("recipe_id")),
            "bounds": list(bounds), "original_known_at": objective.get("known_at"),
            "decision_at": decision, "consumption_scope": scope, "consumption_rule": rule,
            "history_coverage_ok": resolved.coverage_ok, "priority_at_decision": policy.get("priority_at_decision"),
            "visits": visits})
        result.evidence_ids = [str(row.get("event_id")) for row in resolved.rows() if row.get("event_id") is not None]
        return result
    except (AuctionError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O087", str(exc), "parents")


REGISTRATION_OVERRIDES = {f"O{number:03}": globals()[f"o{number:03}"] for number in range(78, 98)}

NATIVE_PRODUCERS = {"O078": native_o078, "O082": native_o082, "O083": native_o083,
                    "O087": native_o087}

_DERIVED_IDS = {"O079", "O080", "O081", *[f"O{number:03}" for number in range(84, 87)],
                "O088", *[f"O{number:03}" for number in range(89, 98)]}
DERIVED_PRODUCERS = {
    recipe_id: (lambda config, parents, recipe_id=recipe_id:
                derived_auction(recipe_id, config, parents))
    for recipe_id in _DERIVED_IDS
}

REQUIRED_INPUTS = {
    "O078": (), "O079": (), "O080": (), "O081": (), "O082": (), "O083": (),
    "O084": (), "O085": (), "O086": (), "O087": (), "O088": (),
    "O089": ("entry", "stop", "target"), "O090": ("lo", "hi"),
    "O091": (), "O092": (), "O093": (), "O094": (), "O095": ("poc",),
    "O096": ("lo", "hi", "direction"), "O097": (),
}


F = OutputField
D, I, S, B, L, M = (Decimal,), (int,), (str,), (bool,), (list,), (dict,)
ND, NI, NS, NB = (D, True), (I, True), (S, True), (B, True)


def _schema(**fields: tuple[tuple[type, ...], bool]) -> dict[str, OutputField]:
    return {name: F(types, nullable) for name, (types, nullable) in fields.items()}


OUTPUT_SCHEMAS = {
    "O078": _schema(profile_id=NS, instrument_id=((str,int),True), instrument_definition_id=NS,
        session_date_et=NS, price_step=ND, construction=NS, as_of=NI, memberships=(M,False),
        count_by_price=(M,False), period_ranges=(L,False), completed_periods=(L,False), a_low=ND,
        a_high=ND, a_period_complete=NB, a_end_at=NI, known_at=NI, coverage_ok=NB,
        event_ids=(L,False), members=(L,True), count=NI),
    "O079": _schema(single_letter_rows=(L,False), interior_band=(L,True), letter_ids=(L,False),
        formation_known_at=NI, repair_state=NS, repaired_rows=(L,False), lower_accepted_id=NS,
        upper_accepted_id=NS, outer_tail_excluded=(B,False)),
    "O080": _schema(side=(S,False), extreme_tail_rows=(L,False), tail_length_rows=(I,False),
        same_letter_tail=(B,False), source_excess=NB, criterion=NS, instrument_id=((str,int),True), grid_id=NS),
    "O081": _schema(poor_high=NB, poor_low=NB, criterion=NS, extreme_price=(D,False),
        tail_length_rows=(I,False), repair_state=NS, side=(S,False), instrument_root=NS, source_grid_compatible=NB),
    "O082": _schema(ibh=ND, ibl=ND, ibw=ND, known_at=NI, upper_extension=ND,
        lower_extension=ND, later_break_flags=(M,True), rth_close_relation=NS, ib_id=NS),
    "O083": _schema(cash_open=ND, open_at=(I,False), as_of=(I,False), crossed_open_by_asof=NB,
        source_open_type=NS, type_known_at=NI, provisional=(B,False), final=NB, path_start=NI,
        path_end=NI, automatic_classifier=((str,dict,bool),True)),
    "O084": _schema(author=NS, taxonomy=NS, provisional_type=NS, provisional_known_at=NI,
        evidence_until=NI, final_type=NS, final_known_at=NI, permission_reference=((str,dict,bool),True),
        automatic_classifier=((str,dict,bool),True)),
    "O085": _schema(author=NS, profile_id=NS, source_shape=NS, subbalance_ids=(L,False),
        connecting_lvn_id=NS, source_permission=((str,dict,bool),True), automatic_shape_direction=NS,
        balance_after_impulse=NB, break_retest_complete=(B,False)),
    "O086": _schema(reference_id=NS, kind=NS, price_or_band=((Decimal,list),False), known_at=NI,
        opening_relation=NS, selected_role=NS, period_id=NS, half_range_gap=ND, half_close_gap=ND),
    "O087": _schema(objective_id=NS, objective_type=NS, bounds=((list,Decimal),True), active_at_decision=NB,
        first_consumption_at=NI, priority_at_decision=((int,str),True), subsequent_outcome=(M,True),
        consumption_scope=NS, consumption_rule=NS, eth_visits_do_not_retire_rth=(B,False)),
    "O088": _schema(source_claim=(M,False), claim_definition_complete=NB, observed_hit_counts=(M,True),
        observed_rate=ND, comparability_holes=(L,False), claim_is_trade_win_rate=(B,False), rounded_hits_inferred=(B,False)),
    "O089": _schema(source_case_id=NS, source_range_reference=((dict,list,Decimal),True), target_distance=(D,False),
        stop_distance=(D,False), source_ambition_ok=NB, automatic_target=((Decimal,dict),True), side=(S,False), rationale_known_at=NI),
    "O090": _schema(balance_id=NS, balance_band=(L,False), edge_id=NS, edge_arrival_at=NI,
        local_confirm_at=NI, rotation_sequence=NB, first_fair_value_event=(M,True), fair_value_id=NS,
        poc_reread=((str,dict,bool),True), later_far_side_objective=((str,dict),True)),
    "O091": _schema(boundary_id=NS, direction=NS, break_at=NI, accept_at=NI, depart_at=NI,
        retest_at=NI, defense_at=NI, initiative_at=NI, break_retest_sequence=NB,
        same_boundary=(B,False), retest_parent_id=NS, ltf_balance_known_at=NI,
        same_boundary_retest_held=NB, buyers_defend_same_imbalance_band=NB),
    "O092": _schema(area_id=NS, value_band=(L,False), outside_before=((str,bool),True), return_at=NI,
        inside_observations=(L,False), acceptance_at=NI, reacceptance_sequence=NB,
        next_objective_id=NS, acceptance_definition=NS, older_value_known_at=NI),
    "O093": _schema(distinct_balances=(B,False), break_at=NI, older_poc_tag_at=NI, reject_at=NI,
        fa_sequence=NB, tagged=NB, source_target_id=NS, source_target_price=ND, rejection_from=NS),
    "O094": _schema(original_value_id=NS, tested_value_id=NS, older_value_known_at=NI,
        explore_at=NI, failure_at=NI,
        return_at=NI, reaccept_at=NI, control_at=NI, saint_fa_sequence=NB,
        current_control_side=NS, older_poc_tag_required=(B,False),route_ok=NB),
    "O095": _schema(profile_id=NS, poc=(D,False), test_ids=(L,False), failed_test_count=(I,False),
        passage_at=NI, held_retest_at=NI, current_poc_read=NS, next_objective_id=NS,
        source_efficient_passage=NB),
    "O096": _schema(balance_id=NS, balance_band=(L,False), direction=(S,False), traverse_start=NI,
        traverse_end=NI, traverse_duration=NI, whole_balance_crossed=(B,False), no_source_hold=NB,
        retest_at=NI, control_at=NI, route_sequence=NB, maximum_duration=NI),
    "O097": _schema(author=NS, htf_thesis_id=NS, htf_side=NS, ltf_side=NS, thesis_alive=NB,
        same_area=(B,False), alignment_ok=NB, confirm_at=NI, htf_area_id=NS,
        local_area_id=NS, free_two_sided_chop=NB, ltf_balance_known_at=NI,
        older_value_known_at=NI),
}


__all__ = ["AuctionError", "DERIVED_PRODUCERS", "NATIVE_PRODUCERS", "OUTPUT_SCHEMAS", "REGISTRATION_OVERRIDES",
           "REQUIRED_INPUTS", "TPOProfile", "build_tpo_profile", "tpo_payload"]
