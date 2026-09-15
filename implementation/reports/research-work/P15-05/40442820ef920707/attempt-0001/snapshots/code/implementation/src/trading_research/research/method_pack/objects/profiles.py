"""Immutable dated auction profiles built from canonical native executions.

This module is deliberately independent of the recipe registry.  The registry
owner can install :data:`REGISTRATION_OVERRIDES` after the legacy recipe
modules have loaded.  Domain constructors accept normalized native members
(the shape emitted by ``adapters.normalize_trade_row`` and
``adapters.normalize_mbp1_row``), rather than caller supplied profile totals.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR
import hashlib
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from trading_research.research.method_pack.clocks import et_ns, ns_to_et
from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult
from trading_research.research.method_pack.contracts import OutputField


PROFILE_KINDS = frozenset({
    "prior_rth", "prior_eth", "overnight", "developing_rth",
    "selected_range", "composite",
})
SIDE_CODES = frozenset({"B", "A", "N"})


class ProfileError(ValueError):
    """The native observations cannot form the claimed profile."""


@dataclass(frozen=True)
class InstrumentDefinition:
    definition_id: str
    instrument_id: str | int
    tick_size: Decimal
    known_at: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "tick_size", dec(self.tick_size))
        if not self.definition_id:
            raise ProfileError("instrument definition_id is required")
        if self.tick_size is None or self.tick_size <= 0:
            raise ProfileError("instrument tick_size must be positive")
        _event_key(self.known_at, "instrument definition known_at")


@dataclass(frozen=True)
class ProfileWindow:
    window_id: str
    kind: str
    session_date: date
    start: int
    end: int
    timezone: str = "America/New_York"
    source_clock_id: str | None = None

    def __post_init__(self) -> None:
        if not self.window_id:
            raise ProfileError("window_id is required")
        if self.kind not in PROFILE_KINDS - {"composite"}:
            raise ProfileError(f"unsupported profile kind {self.kind!r}")
        _event_key(self.start, "profile start")
        _event_key(self.end, "profile end")
        if self.start >= self.end:
            raise ProfileError("profile window must be a nonempty half-open interval")
        if not isinstance(self.session_date, date):
            raise ProfileError("session_date must be a civil date")


@dataclass(frozen=True)
class Coverage:
    """Coverage of a native member interval; absence never means complete."""

    state: str
    start: int | None
    end: int | None
    hole_ids: tuple[str, ...] = ()
    coverage_id: str | None = None

    def __post_init__(self) -> None:
        if self.state not in {"complete", "partial", "unavailable"}:
            raise ProfileError("coverage state must be complete, partial, or unavailable")
        if self.start is not None:
            _event_key(self.start, "coverage start")
        if self.end is not None:
            _event_key(self.end, "coverage end")
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ProfileError("coverage bounds are reversed")
        if self.state == "complete" and (self.start is None or self.end is None):
            raise ProfileError("complete coverage requires explicit bounds")

    def covers(self, start: int, end: int) -> bool:
        return (
            self.state == "complete"
            and self.start is not None
            and self.end is not None
            and self.start <= start
            and self.end >= end
            and not self.hole_ids
        )


@dataclass(frozen=True)
class ValueAreaConfig:
    config_id: str
    fraction: Decimal
    algorithm: str | None
    tie_policy: str | None
    boundary_convention: str = "closed"
    supplied_val: Decimal | None = None
    supplied_vah: Decimal | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "fraction", dec(self.fraction))
        object.__setattr__(self, "supplied_val", dec(self.supplied_val))
        object.__setattr__(self, "supplied_vah", dec(self.supplied_vah))
        if not self.config_id or self.fraction is None or not 0 < self.fraction <= 1:
            raise ProfileError("value-area configuration needs an id and fraction in (0,1]")
        if self.algorithm not in {None, "adjacent_single", "supplied_bounds"}:
            raise ProfileError("unsupported value-area algorithm")
        if self.algorithm == "adjacent_single" and self.tie_policy not in {"lower", "upper"}:
            raise ProfileError("adjacent_single requires an explicit lower/upper tie policy")
        if self.algorithm == "supplied_bounds":
            if self.supplied_val is None or self.supplied_vah is None:
                raise ProfileError("supplied_bounds requires VAL and VAH")
            if self.supplied_val > self.supplied_vah:
                raise ProfileError("supplied value-area bounds are reversed")
        if self.boundary_convention not in {"closed", "left_closed_right_open"}:
            raise ProfileError("unsupported value-area boundary convention")


# The sources disclose these fractions, but not one common platform expansion
# and tie algorithm.  The unresolved policy is data, not an invitation to use
# a legacy greedy default.
SOURCE_VALUE_AREA_CONFIGS = MappingProxyType({
    "common_70": ValueAreaConfig("common_70", Decimal("0.70"), None, None),
    "sires_intraday_40": ValueAreaConfig("sires_intraday_40", Decimal("0.40"), None, None),
    "saint_68": ValueAreaConfig("saint_68", Decimal("0.68"), None, None),
})


@dataclass(frozen=True)
class ProfileDefinition:
    profile_id: str
    instrument: InstrumentDefinition
    window: ProfileWindow
    selection_known_at: int
    source_id: str
    bin_width: Decimal | None = None
    bin_origin: Decimal | None = None
    bin_membership: str = "native_tick"
    poc_tie_policy: str | None = None
    supplied_poc: Decimal | None = None
    value_area: ValueAreaConfig | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "bin_width", dec(self.bin_width))
        object.__setattr__(self, "bin_origin", dec(self.bin_origin))
        object.__setattr__(self, "supplied_poc", dec(self.supplied_poc))
        if not self.profile_id or not self.source_id:
            raise ProfileError("profile_id and source_id are required")
        _event_key(self.selection_known_at, "profile selection known_at")
        if self.bin_membership not in {"native_tick", "lower_closed_upper_open"}:
            raise ProfileError("bin membership must be explicit")
        if self.bin_membership == "native_tick":
            if self.bin_width not in {None, self.instrument.tick_size}:
                raise ProfileError("native-tick bin width must equal the instrument tick")
            object.__setattr__(self, "bin_width", self.instrument.tick_size)
            object.__setattr__(self, "bin_origin", Decimal(0))
        else:
            if self.bin_width is None or self.bin_width <= 0 or self.bin_origin is None:
                raise ProfileError("wider bins require a positive width and explicit origin")
            ticks = self.bin_width / self.instrument.tick_size
            if ticks != ticks.to_integral_value():
                raise ProfileError("bin width must be a whole number of instrument ticks")
        if self.poc_tie_policy not in {None, "lowest", "highest", "supplied"}:
            raise ProfileError("unsupported POC tie policy")
        if self.poc_tie_policy == "supplied" and self.supplied_poc is None:
            raise ProfileError("supplied POC tie policy requires a supplied POC")


@dataclass(frozen=True)
class PriceRow:
    price: Decimal
    buy_volume: Decimal
    sell_volume: Decimal
    unknown_volume: Decimal
    total_volume: Decimal
    known_delta: Decimal
    full_delta: Decimal | None
    delta_low: Decimal
    delta_high: Decimal


@dataclass(frozen=True)
class ProfileSnapshot:
    snapshot_id: str
    profile_id: str
    kind: str
    instrument_id: str | int
    instrument_definition_id: str
    tick_size: Decimal
    session_date: date | None
    window_id: str
    formation_start: int
    formation_end: int
    as_of: int
    known_at: int
    rows: tuple[PriceRow, ...]
    total_volume: Decimal
    H: Decimal | None
    L: Decimal | None
    poc: Decimal | None
    poc_candidates: tuple[Decimal, ...]
    poc_tie_state: str
    val: Decimal | None
    vah: Decimal | None
    value_area_fraction: Decimal | None
    value_area_config_id: str | None
    value_area_algorithm: str | None
    value_area_tie_policy: str | None
    volume_inside_value: Decimal | None
    achieved_value_fraction: Decimal | None
    coverage_state: str
    coverage_ok: bool | None
    coverage_holes: tuple[str, ...]
    event_ids: tuple[str, ...]
    parent_ids: tuple[str, ...] = ()
    source_id: str | None = None
    selection_rationale: str | None = None
    bin_width: Decimal | None = None
    bin_origin: Decimal | None = None
    bin_membership: str | None = None

    def row(self, price: Decimal | int | str) -> PriceRow | None:
        target = dec(price)
        return next((row for row in self.rows if row.price == target), None)


@dataclass(frozen=True)
class ProfileReference:
    reference_id: str
    profile_id: str
    snapshot_id: str
    role: str
    price: Decimal
    known_at: int
    contact_rule: str = "exact"

    def __post_init__(self) -> None:
        object.__setattr__(self, "price", dec(self.price))
        if not self.reference_id or not self.profile_id or not self.snapshot_id:
            raise ProfileError("reference identity is required")
        _event_key(self.known_at, "reference known_at")
        if self.contact_rule != "exact":
            raise ProfileError("only exact native-price contact is implemented")


def sires_overnight_window(session_date: date) -> ProfileWindow:
    """O011-bound 18:00 previous day through 09:30 ET window."""

    previous = session_date - timedelta(days=1)
    return ProfileWindow(
        window_id=f"sires-overnight:{session_date.isoformat()}",
        kind="overnight",
        session_date=session_date,
        start=et_ns(previous, 18),
        end=et_ns(session_date, 9, 30),
        source_clock_id="O011:sires_overnight_1800_0930_et",
    )


def _event_key(value: Any, label: str) -> int:
    if type(value) is not int:
        raise ProfileError(f"{label} must be an integer UTC nanosecond key")
    return value


def _required_decimal(value: Any, label: str) -> Decimal:
    result = dec(value)
    if result is None or not result.is_finite():
        raise ProfileError(f"{label} must be a finite numeric value")
    return result


def _coverage_holes(coverage: Coverage, start: int, end: int) -> tuple[str, ...]:
    holes = list(coverage.hole_ids)
    if not coverage.covers(start, end) and not holes:
        holes.append("HOLE:data_coverage")
    return tuple(dict.fromkeys(holes))


def _bin_price(definition: ProfileDefinition, price: Decimal) -> Decimal:
    tick = definition.instrument.tick_size
    ticks = price / tick
    if ticks != ticks.to_integral_value():
        raise ProfileError(f"price {price} is not aligned to definition tick {tick}")
    if definition.bin_membership == "native_tick":
        return price
    assert definition.bin_origin is not None and definition.bin_width is not None
    index = ((price - definition.bin_origin) / definition.bin_width).to_integral_value(rounding=ROUND_FLOOR)
    return definition.bin_origin + index * definition.bin_width


def _native_trade(member: Mapping[str, Any], definition: ProfileDefinition) -> tuple[str, int, int, Decimal, Decimal, str] | None:
    action = str(member.get("action") or "").upper()
    is_trade = member.get("is_trade")
    if action != "T" and is_trade is not True:
        return None
    required = ("event_id", "dataset_id", "instrument_id", "event_ns", "known_at", "price")
    missing = [key for key in required if member.get(key) is None]
    if missing:
        raise ProfileError(f"native execution lacks {','.join(missing)}")
    if member["instrument_id"] != definition.instrument.instrument_id:
        raise ProfileError("execution instrument does not match profile definition")
    dataset_id = str(member["dataset_id"]).lower()
    if "trades" not in dataset_id and "mbp-1" not in dataset_id:
        raise ProfileError("profile members must come from a canonical execution dataset")
    if member.get("source_precision") != "nanoseconds":
        raise ProfileError("profile members must retain native nanosecond precision")
    event_ns = _event_key(member["event_ns"], "execution event_ns")
    known_at = _event_key(member["known_at"], "execution known_at")
    if known_at < event_ns:
        raise ProfileError("execution known_at precedes event time")
    raw_size = member.get("executed_size", member.get("size"))
    if raw_size is None or isinstance(raw_size, bool):
        raise ProfileError("native execution lacks size")
    size = dec(raw_size)
    if size is None or size < 0 or size != size.to_integral_value():
        raise ProfileError("native execution size must be a nonnegative integer")
    price = dec(member["price"])
    if price is None:
        raise ProfileError("native execution lacks price")
    side = str(member.get("side") or "").upper()
    if side not in SIDE_CODES:
        raise ProfileError("canonical execution side must be B, A, or N")
    return str(member["event_id"]), event_ns, known_at, price, size, side


def _poc(rows: Sequence[PriceRow], tie_policy: str | None, supplied_poc: Decimal | None = None) -> tuple[Decimal | None, tuple[Decimal, ...], str]:
    if not rows or all(row.total_volume == 0 for row in rows):
        return None, (), "empty"
    maximum = max(row.total_volume for row in rows)
    candidates = tuple(row.price for row in rows if row.total_volume == maximum)
    if len(candidates) == 1:
        return candidates[0], candidates, "unique"
    selected = None
    if tie_policy == "lowest":
        selected = candidates[0]
    elif tie_policy == "highest":
        selected = candidates[-1]
    elif tie_policy == "supplied" and supplied_poc in candidates:
        selected = supplied_poc
    return selected, candidates, "resolved" if selected is not None else "unresolved"


def _value_area(rows: Sequence[PriceRow], poc: Decimal | None, config: ValueAreaConfig | None) -> tuple[Decimal | None, Decimal | None, Decimal | None, Decimal | None]:
    if config is None or not rows or config.algorithm is None:
        return None, None, None, None
    total = sum((row.total_volume for row in rows), Decimal(0))
    if total <= 0:
        return None, None, None, None
    if config.algorithm == "supplied_bounds":
        assert config.supplied_val is not None and config.supplied_vah is not None
        selected = [row for row in rows if config.supplied_val <= row.price and (
            row.price <= config.supplied_vah if config.boundary_convention == "closed" else row.price < config.supplied_vah
        )]
        inside = sum((row.total_volume for row in selected), Decimal(0))
        return config.supplied_val, config.supplied_vah, inside, inside / total
    if poc is None:
        return None, None, None, None
    index = next(i for i, row in enumerate(rows) if row.price == poc)
    selected = {index}
    inside = rows[index].total_volume
    low = index - 1
    high = index + 1
    while inside / total < config.fraction and (low >= 0 or high < len(rows)):
        low_volume = rows[low].total_volume if low >= 0 else None
        high_volume = rows[high].total_volume if high < len(rows) else None
        if low_volume is None:
            chosen = high
        elif high_volume is None:
            chosen = low
        elif low_volume > high_volume:
            chosen = low
        elif high_volume > low_volume:
            chosen = high
        else:
            chosen = low if config.tie_policy == "lower" else high
        selected.add(chosen)
        inside += rows[chosen].total_volume
        if chosen == low:
            low -= 1
        else:
            high += 1
    val = rows[min(selected)].price
    vah = rows[max(selected)].price
    return val, vah, inside, inside / total


def build_profile(
    definition: ProfileDefinition,
    members: Iterable[Mapping[str, Any]],
    *,
    as_of: int,
    coverage: Coverage,
) -> ProfileSnapshot:
    """Build an immutable profile from validated native execution members."""

    _event_key(as_of, "profile as_of")
    if as_of < definition.window.start:
        raise ProfileError("profile as_of precedes its formation window")
    cutoff = min(as_of, definition.window.end)
    covered = coverage.covers(definition.window.start, cutoff)
    accum: dict[Decimal, list[Decimal]] = {}
    member_ids: list[str] = []
    event_times: list[int] = []
    # A snapshot records the state assessed at ``as_of`` even when tape
    # coverage is unknown.  That assessment itself cannot be available before
    # its cutoff, and a completed historical window viewed later retains the
    # later snapshot availability.
    availability = [definition.selection_known_at, definition.instrument.known_at, as_of]
    native_high: Decimal | None = None
    native_low: Decimal | None = None
    seen: set[str] = set()
    for member in members:
        parsed = _native_trade(member, definition)
        if parsed is None:
            continue
        event_id, event_ns, known_at, price, size, side = parsed
        if not definition.window.start <= event_ns < cutoff:
            continue
        if event_id in seen:
            raise ProfileError(f"duplicate canonical execution ownership: {event_id}")
        seen.add(event_id)
        binned = _bin_price(definition, price)
        row = accum.setdefault(binned, [Decimal(0), Decimal(0), Decimal(0)])
        row[{"B": 0, "A": 1, "N": 2}[side]] += size
        member_ids.append(event_id)
        event_times.append(event_ns)
        availability.append(known_at)
        native_high = price if native_high is None else max(native_high, price)
        native_low = price if native_low is None else min(native_low, price)
    if covered and accum:
        assert definition.bin_width is not None
        price = min(accum)
        maximum_price = max(accum)
        while price <= maximum_price:
            accum.setdefault(price, [Decimal(0), Decimal(0), Decimal(0)])
            price += definition.bin_width
    rows: list[PriceRow] = []
    for price in sorted(accum):
        buy, sell, unknown = accum[price]
        known_delta = buy - sell
        rows.append(PriceRow(
            price, buy, sell, unknown, buy + sell + unknown,
            known_delta, known_delta if unknown == 0 else None,
            known_delta - unknown, known_delta + unknown,
        ))
    poc, candidates, tie_state = _poc(rows, definition.poc_tie_policy, definition.supplied_poc)
    val, vah, volume_inside, achieved = _value_area(rows, poc, definition.value_area)
    total = sum((row.total_volume for row in rows), Decimal(0))
    if any(row.buy_volume + row.sell_volume + row.unknown_volume != row.total_volume for row in rows):
        raise AssertionError("profile row side-volume reconciliation failed")
    holes = _coverage_holes(coverage, definition.window.start, cutoff)
    if definition.value_area is not None and definition.value_area.algorithm is None:
        holes = tuple(dict.fromkeys((*holes, "HOLE:O062:construction")))
    if tie_state == "unresolved":
        holes = tuple(dict.fromkeys((*holes, "HOLE:O064:tie_rule")))
    if (definition.value_area is not None and definition.value_area.algorithm == "supplied_bounds"
            and achieved is not None and achieved < definition.value_area.fraction):
        holes = tuple(dict.fromkeys((*holes, "HOLE:O062:fraction_coverage")))
    known_at = max(availability)
    digest = hashlib.sha256()
    digest.update(definition.profile_id.encode())
    digest.update(str(cutoff).encode())
    for event_id in member_ids:
        digest.update(b"\0")
        digest.update(event_id.encode())
    snapshot_id = f"{definition.profile_id}@{cutoff}:{digest.hexdigest()[:16]}"
    return ProfileSnapshot(
        snapshot_id=snapshot_id,
        profile_id=definition.profile_id,
        kind=definition.window.kind,
        instrument_id=definition.instrument.instrument_id,
        instrument_definition_id=definition.instrument.definition_id,
        tick_size=definition.instrument.tick_size,
        session_date=definition.window.session_date,
        window_id=definition.window.window_id,
        formation_start=definition.window.start,
        formation_end=cutoff,
        as_of=as_of,
        known_at=known_at,
        rows=tuple(rows),
        total_volume=total,
        H=native_high,
        L=native_low,
        poc=poc,
        poc_candidates=candidates,
        poc_tie_state=tie_state,
        val=val,
        vah=vah,
        value_area_fraction=None if definition.value_area is None else definition.value_area.fraction,
        value_area_config_id=None if definition.value_area is None else definition.value_area.config_id,
        value_area_algorithm=None if definition.value_area is None else definition.value_area.algorithm,
        value_area_tie_policy=None if definition.value_area is None else definition.value_area.tie_policy,
        volume_inside_value=volume_inside,
        achieved_value_fraction=achieved,
        coverage_state=coverage.state,
        coverage_ok=True if covered else None,
        coverage_holes=holes,
        event_ids=tuple(member_ids),
        source_id=definition.source_id,
        bin_width=definition.bin_width,
        bin_origin=definition.bin_origin,
        bin_membership=definition.bin_membership,
    )


def compose_profiles(
    *,
    composite_id: str,
    profiles: Sequence[ProfileSnapshot],
    selection_known_at: int,
    rationale: str | None,
) -> ProfileSnapshot:
    """Sum explicit compatible constituents after validating ownership."""

    _event_key(selection_known_at, "composite selection_known_at")
    if not profiles:
        raise ProfileError("a composite requires explicit constituent profiles")
    if not composite_id:
        raise ProfileError("composite_id is required")
    first = profiles[0]
    for profile in profiles[1:]:
        if (profile.instrument_id, profile.instrument_definition_id, profile.tick_size,
                profile.bin_width, profile.bin_origin, profile.bin_membership) != (
                first.instrument_id, first.instrument_definition_id, first.tick_size,
                first.bin_width, first.bin_origin, first.bin_membership):
            raise ProfileError("composite constituents have incompatible instrument/grid identity")
    owned: set[str] = set()
    for profile in profiles:
        duplicate = owned.intersection(profile.event_ids)
        if duplicate:
            raise ProfileError(f"composite has overlapping canonical event ownership: {sorted(duplicate)[0]}")
        owned.update(profile.event_ids)
    sums: dict[Decimal, list[Decimal]] = {}
    for profile in profiles:
        for row in profile.rows:
            target = sums.setdefault(row.price, [Decimal(0), Decimal(0), Decimal(0)])
            target[0] += row.buy_volume
            target[1] += row.sell_volume
            target[2] += row.unknown_volume
    rows = tuple(PriceRow(
        price, values[0], values[1], values[2], sum(values, Decimal(0)),
        values[0] - values[1],
        values[0] - values[1] if values[2] == 0 else None,
        values[0] - values[1] - values[2], values[0] - values[1] + values[2],
    ) for price, values in sorted(sums.items()))
    poc, candidates, tie_state = _poc(rows, None)
    coverage_ok = True if all(profile.coverage_ok is True for profile in profiles) else None
    holes = tuple(dict.fromkeys(hole for profile in profiles for hole in profile.coverage_holes))
    if rationale is None:
        holes = tuple(dict.fromkeys((*holes, "HOLE:O070:selector")))
    if tie_state == "unresolved":
        holes = tuple(dict.fromkeys((*holes, "HOLE:O064:tie_rule")))
    known_at = max(selection_known_at, *(profile.known_at for profile in profiles))
    digest = hashlib.sha256("\0".join(profile.snapshot_id for profile in profiles).encode()).hexdigest()[:16]
    return ProfileSnapshot(
        snapshot_id=f"{composite_id}@{known_at}:{digest}", profile_id=composite_id,
        kind="composite", instrument_id=first.instrument_id,
        instrument_definition_id=first.instrument_definition_id, tick_size=first.tick_size,
        session_date=None, window_id=f"composite:{composite_id}",
        formation_start=min(profile.formation_start for profile in profiles),
        formation_end=max(profile.formation_end for profile in profiles),
        as_of=max(profile.as_of for profile in profiles), known_at=known_at,
        rows=rows, total_volume=sum((row.total_volume for row in rows), Decimal(0)),
        H=max((profile.H for profile in profiles if profile.H is not None), default=None),
        L=min((profile.L for profile in profiles if profile.L is not None), default=None),
        poc=poc, poc_candidates=candidates, poc_tie_state=tie_state,
        val=None, vah=None, value_area_fraction=None, value_area_config_id=None,
        value_area_algorithm=None, value_area_tie_policy=None,
        volume_inside_value=None, achieved_value_fraction=None,
        coverage_state="complete" if coverage_ok else "partial", coverage_ok=coverage_ok,
        coverage_holes=holes, event_ids=tuple(sorted(owned)),
        parent_ids=tuple(profile.snapshot_id for profile in profiles),
        source_id=first.source_id, selection_rationale=rationale, bin_width=first.bin_width,
        bin_origin=first.bin_origin, bin_membership=first.bin_membership,
    )


def snapshot_payload(profile: ProfileSnapshot) -> dict[str, Any]:
    """Return a complete mutable recipe payload without exposing internals."""

    rows = [asdict(row) for row in profile.rows]
    native = {str(row.price): row.total_volume for row in profile.rows}
    return {
        "snapshot_id": profile.snapshot_id,
        "profile_id": profile.profile_id,
        "kind": profile.kind,
        "instrument_id": profile.instrument_id,
        "instrument_definition_id": profile.instrument_definition_id,
        "tick_size": profile.tick_size,
        "session_date": None if profile.session_date is None else profile.session_date.isoformat(),
        "window_id": profile.window_id,
        "formation_start": profile.formation_start,
        "formation_end": profile.formation_end,
        "as_of": profile.as_of,
        "known_at": profile.known_at,
        "rows": rows,
        "volume_histogram": native,
        "native_volume_by_price": native,
        "source_bins": rows,
        "total": profile.total_volume,
        "total_volume": profile.total_volume,
        "H": profile.H,
        "L": profile.L,
        "poc": profile.poc,
        "poc_candidates": list(profile.poc_candidates),
        "poc_tie_state": profile.poc_tie_state,
        "val": profile.val,
        "vah": profile.vah,
        "value_area_fraction": profile.value_area_fraction,
        "value_area_config_id": profile.value_area_config_id,
        "value_area_algorithm": profile.value_area_algorithm,
        "value_area_tie_policy": profile.value_area_tie_policy,
        "volume_inside_value": profile.volume_inside_value,
        "achieved_value_fraction": profile.achieved_value_fraction,
        "coverage": {
            "state": profile.coverage_state,
            "ok": profile.coverage_ok,
            "holes": list(profile.coverage_holes),
        },
        "coverage_ok": profile.coverage_ok,
        "event_ids": list(profile.event_ids),
        "parent_ids": list(profile.parent_ids),
        "source_id": profile.source_id,
        "selection_rationale": profile.selection_rationale,
        "bin_width": profile.bin_width,
        "bin_origin": profile.bin_origin,
        "bin_membership": profile.bin_membership,
    }


def _result(recipe_id: str, profile: ProfileSnapshot, value: dict[str, Any] | None = None, *, holes: Sequence[str] = ()) -> RecipeResult:
    all_holes = list(dict.fromkeys((*profile.coverage_holes, *holes)))
    payload = snapshot_payload(profile) if value is None else value
    return RecipeResult(
        recipe_id, "computed" if not all_holes else "hole", payload,
        hole_ids=all_holes, known_at=profile.known_at, base_ok=True,
        coverage_ok=profile.coverage_ok, parent_ids=list(profile.parent_ids),
        evidence_ids=list(profile.event_ids),
    )


def _invalid(recipe_id: str, exc: Exception) -> RecipeResult:
    return RecipeResult(recipe_id, "invalid", {}, [f"HOLE:{recipe_id}:native_members"],
                        base_ok=False, coverage_ok=None, reason=str(exc))


def _profile_input(inp: Mapping[str, Any]) -> ProfileSnapshot:
    profile = inp.get("profile")
    if isinstance(profile, ProfileSnapshot):
        return profile
    definition = inp.get("profile_definition")
    if not isinstance(definition, ProfileDefinition):
        raise ProfileError("profile_definition is required for native construction")
    coverage = inp.get("coverage")
    if not isinstance(coverage, Coverage):
        coverage = Coverage("unavailable", None, None, ("HOLE:data_coverage",))
    members = inp.get("resolved_members", inp.get("events"))
    if members is None:
        raise ProfileError("resolved native members are required")
    as_of = inp.get("as_of", definition.window.end)
    return build_profile(definition, members, as_of=as_of, coverage=coverage)


def o061(inp: dict) -> RecipeResult:
    try:
        if "profile_definition" in inp or isinstance(inp.get("profile"), ProfileSnapshot):
            return _result("O061", _profile_input(inp))
        # Compatibility arithmetic remains explicitly incomplete and cannot be
        # admitted as a dated source profile.
        bins: dict[str, Decimal] = {}
        for trade in inp.get("trades", ()):
            if trade.get("is_quote"):
                continue
            key = "agg" if inp.get("bin_lo") is not None else str(dec(trade["price"]))
            if key == "agg" and not dec(inp["bin_lo"]) <= dec(trade["price"]) < dec(inp["bin_hi"]):
                continue
            bins[key] = bins.get(key, Decimal(0)) + dec(trade["size"])
        return RecipeResult("O061", "hole", {"bins": bins, "native_volume_by_price": bins,
            "total": sum(bins.values(), Decimal(0)), "total_volume": sum(bins.values(), Decimal(0)),
            "profile_id": None, "coverage": {"state": "unavailable", "ok": None}, "as_of": inp.get("as_of")},
            ["HOLE:O061:profile_definition", "HOLE:O061:native_members"], inp.get("known_at"), True, None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O061", exc)


def o062(inp: dict) -> RecipeResult:
    try:
        if isinstance(inp.get("profile"), ProfileSnapshot):
            profile = inp["profile"]
            value = {"val": profile.val, "vah": profile.vah,
                "fraction": profile.value_area_fraction,
                "volume_inside": profile.volume_inside_value,
                "achieved_fraction": profile.achieved_value_fraction,
                "construction_known": profile.value_area_algorithm is not None,
                "config_id": profile.value_area_config_id,
                "algorithm": profile.value_area_algorithm,
                "tie_policy": profile.value_area_tie_policy,
                "profile_id": profile.profile_id, "snapshot_id": profile.snapshot_id}
            holes = [] if profile.value_area_algorithm is not None else ["HOLE:O062:construction"]
            return _result("O062", profile, value, holes=holes)
        bins = inp.get("bins")
        total = dec(inp.get("total"))
        covered = dec(inp.get("covered"))
        val, vah = dec(inp.get("val")), dec(inp.get("vah"))
        if bins is not None:
            histogram = {dec(k): dec(v) for k, v in bins.items()}
            if any(v < 0 for v in histogram.values()):
                raise ProfileError("negative profile volume")
            total = sum(histogram.values(), Decimal(0))
            convention = inp.get("boundary_convention")
            if val is not None and vah is not None and convention in {"closed", "left_closed_right_open"}:
                covered = sum((v for p, v in histogram.items() if val <= p and (p <= vah if convention == "closed" else p < vah)), Decimal(0))
        if total is None or covered is None:
            return RecipeResult("O062", "hole", {"achieved_fraction": None, "val": val, "vah": vah},
                [f"HOLE:O062:{'total' if total is None else 'covered'}"], inp.get("known_at"), None, None)
        if total == 0:
            return RecipeResult("O062", "hole", {"val": val, "vah": vah, "fraction": dec(inp.get("required_fraction")),
                "volume_inside": covered, "achieved_fraction": None, "meets_required": None,
                "construction_known": False},
                ["HOLE:O062:positive_volume"], inp.get("known_at"), None, None)
        if total < 0 or covered < 0 or covered > total:
            return RecipeResult("O062", "invalid", {"val": val, "vah": vah,
                "fraction": dec(inp.get("required_fraction")), "volume_inside": covered,
                "achieved_fraction": None, "meets_required": None,
                "construction_known": False}, ["HOLE:O062:coverage_volumes"],
                inp.get("known_at"), False, None, reason="invalid profile coverage volumes")
        fraction = dec(inp.get("required_fraction"))
        achieved = covered / total
        return RecipeResult("O062", "hole", {"val": val, "vah": vah, "fraction": fraction,
            "volume_inside": covered, "achieved_fraction": achieved,
            "meets_required": None if fraction is None else achieved >= fraction,
            "construction_known": False}, ["HOLE:O062:construction"], inp.get("known_at"), True, None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O062", exc)


def o063(inp: dict) -> RecipeResult:
    try:
        if "profile_definition" in inp or isinstance(inp.get("profile"), ProfileSnapshot):
            profile = _profile_input(inp)
            if profile.kind != "developing_rth":
                raise ProfileError("O063 requires a developing_rth profile")
            return _result("O063", profile)
        eligible = [snap for snap in inp.get("snapshots", ()) if snap.get("known_at") <= inp["as_of"]]
        if not eligible:
            return RecipeResult("O063", "hole", {"poc": None}, ["HOLE:O063:snapshot"], coverage_ok=None)
        chosen = eligible[-1]
        required = ("snapshot_id", "volume_histogram", "H", "L", "as_of")
        holes = [f"HOLE:O063:{key}" for key in required if chosen.get(key) is None]
        return RecipeResult("O063", "hole" if holes else "computed", {**chosen,
            "snapshot_known_at": chosen["known_at"], "mutated": False}, holes,
            chosen["known_at"], True, None if holes else True)
    except (ProfileError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O063", exc)


def o064(inp: dict) -> RecipeResult:
    try:
        if isinstance(inp.get("profile"), ProfileSnapshot):
            profile = inp["profile"]
            maximum = max((row.total_volume for row in profile.rows), default=None)
            value = {"max": maximum, "max_volume": maximum, "poc": profile.poc,
                "poc_price_or_band": profile.poc, "poc_candidates": list(profile.poc_candidates),
                "tie_state": profile.poc_tie_state, "tied": len(profile.poc_candidates) > 1,
                "profile_id": profile.profile_id, "snapshot_id": profile.snapshot_id}
            holes = ["HOLE:O064:tie_rule"] if profile.poc_tie_state == "unresolved" else []
            return _result("O064", profile, value, holes=holes)
        bins = {dec(k): dec(v) for k, v in inp.get("bins", {}).items()}
        if any(v < 0 for v in bins.values()):
            raise ProfileError("negative profile volume")
        rows = tuple(PriceRow(p, v, Decimal(0), Decimal(0), v, v, v, v, v) for p, v in sorted(bins.items()))
        poc, candidates, state = _poc(rows, inp.get("tie_rule"), dec(inp.get("supplied_poc")))
        maximum = max(bins.values()) if bins else None
        holes = [] if state in {"unique", "resolved"} else ["HOLE:O064:positive_volume" if state == "empty" else "HOLE:O064:tie_rule"]
        return RecipeResult("O064", "computed" if not holes else "hole", {"poc": poc, "max": maximum,
            "max_volume": maximum, "poc_candidates": list(candidates), "poc_price_or_band": poc,
            "tie_state": state, "tied": len(candidates) > 1, "mid_is_poc_formula": False},
            holes, inp.get("known_at"), True if rows else None, True if rows and not holes else None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O064", exc)


def o065(inp: dict) -> RecipeResult:
    try:
        reference = inp.get("reference")
        identity_holes = []
        if isinstance(reference, ProfileReference):
            reference_id = reference.reference_id
            profile_id = reference.profile_id
            snapshot_id = reference.snapshot_id
            reference_price = reference.price
            reference_known_at = reference.known_at
        else:
            # The scalar route is a useful arithmetic helper for printed
            # fixtures, but it is not evidence of a dated profile reference.
            # Preserve absent identities as absent instead of assigning names
            # that could later pass an identity join.
            reference_id = inp.get("reference_id")
            profile_id = inp.get("profile_id")
            snapshot_id = inp.get("snapshot_id")
            reference_price = _required_decimal(inp.get("poc"), "reference POC")
            reference_known_at = _event_key(
                inp.get("reference_known_at", inp.get("known_at")),
                "reference known_at",
            )
            for field, value in (
                ("reference_id", reference_id),
                ("profile_id", profile_id),
                ("snapshot_id", snapshot_id),
            ):
                if not isinstance(value, str) or not value:
                    identity_holes.append(f"HOLE:O065:{field}")
        decision = _event_key(inp["as_of"], "reference decision as_of")
        coverage = inp.get("coverage")
        legacy_complete = inp.get("coverage_complete")
        coverage_ok = (True if coverage.covers(reference_known_at, decision) else None) if isinstance(coverage, Coverage) else (True if legacy_complete is True else None)
        visits = []
        for event in inp.get("resolved_members", inp.get("visits", ())):
            t = event.get("event_ns", event.get("t"))
            price = dec(event.get("price"))
            event_id = event.get("event_id") or event.get("id")
            if t is not None:
                t = _event_key(t, "visit event_ns")
            if t is not None and reference_known_at <= t <= decision and price == reference_price:
                if not isinstance(event_id, str) or not event_id:
                    identity_holes.append("HOLE:O065:visit_identity")
                visit_known_at = event.get("known_at", t)
                if type(visit_known_at) is not int:
                    identity_holes.append("HOLE:O065:visit_known_at")
                visits.append({"event_id": event_id, "event_ns": t,
                               "known_at": visit_known_at, "price": price})
        visits.sort(key=lambda row: (row["event_ns"], row["event_id"] or ""))
        untested = False if visits else (True if coverage_ok is True else None)
        holes = list(identity_holes)
        if not visits and coverage_ok is not True:
            holes.append("HOLE:O065:coverage")
        holes = list(dict.fromkeys(holes))
        return RecipeResult("O065", "computed" if not holes else "hole", {
            "untested": untested, "untested_at_decision": untested,
            "first_qualifying_visit": visits[0] if visits else None,
            "active_reference_id": reference_id, "poc": reference_price,
            "profile_id": profile_id, "snapshot_id": snapshot_id,
        }, holes, (max(reference_known_at, *(row["known_at"] for row in visits))
                   if visits and all(type(row["known_at"]) is int for row in visits)
                   else None if visits
                   else decision if coverage_ok is True else reference_known_at),
            True, coverage_ok)
    except (ProfileError, KeyError, TypeError, ValueError) as exc:
        return _invalid("O065", exc)


def _selected_rows(profile: ProfileSnapshot, bounds: Sequence[Any]) -> list[PriceRow]:
    lo, hi = dec(bounds[0]), dec(bounds[1])
    if lo > hi:
        raise ProfileError("selected profile bounds are reversed")
    return [row for row in profile.rows if lo <= row.price <= hi]


def o066(inp: dict) -> RecipeResult:
    try:
        profile = inp.get("profile")
        node = inp.get("node", inp.get("hvn_band"))
        if node is None:
            return RecipeResult("O066", "hole", {"hvn_band": None, "automatic_node_selection": None}, ["HOLE:O066:selector"], coverage_ok=None)
        if isinstance(profile, ProfileSnapshot):
            rows = _selected_rows(profile, node)
            maximum = max((row.total_volume for row in rows), default=None)
            peaks = [row.price for row in rows if row.total_volume == maximum]
            value = {"hvn_band": [dec(node[0]), dec(node[1])], "node_volume": sum((r.total_volume for r in rows), Decimal(0)),
                "volume": sum((r.total_volume for r in rows), Decimal(0)), "peak_candidates": peaks,
                "source_node_known": inp.get("source_node_known") is True,
                "automatic_node_selection": None, "profile_id": profile.profile_id,
                "snapshot_id": profile.snapshot_id, "node_id": inp.get("node_id")}
            holes = [] if inp.get("source_node_known") is True else ["HOLE:O066:selector"]
            return _result("O066", profile, value, holes=holes)
        volumes = [dec(v) for v in inp.get("volumes", ())]
        other = inp.get("reaction")
        overlap = None if not other else [max(dec(node[0]), dec(other[0])), min(dec(node[1]), dec(other[1]))]
        if overlap and overlap[0] > overlap[1]: overlap = None
        return RecipeResult("O066", "hole", {"node": [dec(node[0]), dec(node[1])], "volume": sum(volumes, Decimal(0)),
            "peak": inp.get("peak"), "overlap": overlap, "automatic_node_selection": None}, ["HOLE:O066:profile"], inp.get("known_at"), True, None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O066", exc)


def o067(inp: dict) -> RecipeResult:
    try:
        profile = inp.get("profile")
        bridge = inp.get("bridge_band")
        if isinstance(profile, ProfileSnapshot) and bridge is not None:
            if inp.get("accepted_a_id") == inp.get("accepted_b_id") or not inp.get("accepted_a_id") or not inp.get("accepted_b_id"):
                raise ProfileError("LVN requires two distinct accepted-area identities")
            rows = _selected_rows(profile, bridge)
            minimum = min((row.total_volume for row in rows), default=None)
            troughs = [row.price for row in rows if row.total_volume == minimum]
            value = {"bridge_band": [dec(bridge[0]), dec(bridge[1])],
                "bridge_volume": sum((r.total_volume for r in rows), Decimal(0)),
                "trough_candidates": troughs, "accepted_area_ids": [inp["accepted_a_id"], inp["accepted_b_id"]],
                "transition_ids": list(inp.get("transition_ids", ())), "automatic_node_selection": None,
                "profile_id": profile.profile_id, "snapshot_id": profile.snapshot_id}
            holes = [] if inp.get("source_node_known") is True else ["HOLE:O067:selector"]
            return _result("O067", profile, value, holes=holes)
        if inp.get("accepted_b") is None:
            return RecipeResult("O067", "hole", {"bridge_volume": None}, ["HOLE:O067:accepted_area"], base_ok=None, coverage_ok=None)
        return RecipeResult("O067", "hole", {"bridge_volume": sum((dec(v) for v in inp.get("bridge_volumes", ())), Decimal(0)),
            "trough": inp.get("trough"), "automatic_node_selection": None}, ["HOLE:O067:profile"], inp.get("known_at"), True, None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O067", exc)


def o068(inp: dict) -> RecipeResult:
    try:
        profile, shelf = inp.get("profile"), inp.get("shelf", inp.get("shelf_band"))
        if shelf is None:
            return RecipeResult("O068", "hole", {"automatic_shelf_selection": None}, ["HOLE:O068:selector"], coverage_ok=None)
        if isinstance(profile, ProfileSnapshot):
            rows = _selected_rows(profile, shelf)
            transition = inp.get("transition_band")
            transition_rows = [] if transition is None else _selected_rows(profile, transition)
            value = {"shelf_band": [dec(shelf[0]), dec(shelf[1])], "shelf_id": inp.get("shelf_id"),
                "shelf_volume": sum((r.total_volume for r in rows), Decimal(0)),
                "transition_band": None if transition is None else [dec(transition[0]), dec(transition[1])],
                "transition_volume": sum((r.total_volume for r in transition_rows), Decimal(0)),
                "edge_id": inp.get("edge_id"), "automatic_shelf_selection": None,
                "ratio_defines_ledge": False, "profile_id": profile.profile_id, "snapshot_id": profile.snapshot_id}
            holes = [] if inp.get("source_shelf_known") is True and transition is not None and inp.get("edge_id") else ["HOLE:O068:selector"]
            return _result("O068", profile, value, holes=holes)
        return RecipeResult("O068", "hole", {"shelf": [dec(shelf[0]), dec(shelf[1])],
            "shelf_volume": sum((dec(v) for v in inp.get("shelf_volumes", ())), Decimal(0)),
            "transition_volume": sum((dec(v) for v in inp.get("transition_volumes", ())), Decimal(0)),
            "ratio_defines_ledge": False}, ["HOLE:O068:profile"], inp.get("known_at"), True, None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O068", exc)


def o069(inp: dict) -> RecipeResult:
    try:
        ledge_id, retest_id = inp.get("ledge_id"), inp.get("retest_ledge_id")
        ledge, retest = dec(inp.get("ledge_px")), dec(inp.get("retest_px"))
        same_id = ledge_id == retest_id if ledge_id is not None and retest_id is not None else None
        same_price = None if ledge is None or retest is None else ledge == retest
        # Legacy values can show geometric equality, but cannot certify stable identity.
        value = {"same_id": same_id if ledge_id is not None or retest_id is not None else same_price,
            "same_price": same_price, "ledge_id": ledge_id, "retest_ledge_id": retest_id,
            "vah_touch_is_retest": False if dec(inp.get("dev_vah")) is None or retest is None else dec(inp.get("dev_vah")) == retest and same_id is True}
        holes = [] if ledge_id is not None and retest_id is not None else ["HOLE:O069:identity"]
        return RecipeResult("O069", "computed" if not holes else "hole", value, holes, inp.get("known_at"), True, None if holes else True)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O069", exc)


def o070(inp: dict) -> RecipeResult:
    try:
        profiles = inp.get("profiles", ())
        if profiles and all(isinstance(profile, ProfileSnapshot) for profile in profiles):
            composite = compose_profiles(composite_id=inp.get("composite_id", "composite"), profiles=profiles,
                selection_known_at=inp.get("selection_known_at", inp.get("known_at")), rationale=inp.get("rationale"))
            value = snapshot_payload(composite)
            value["composite"] = value["volume_histogram"]
            value["composite_histogram"] = value["volume_histogram"]
            value["constituent_ids"] = list(composite.parent_ids)
            value["automatic_window_selection"] = None
            return _result("O070", composite, value)
        if inp.get("overlap"):
            return RecipeResult("O070", "hole", {"total": None, "composite": None, "automatic_window_selection": None}, ["HOLE:O070:overlap"], coverage_ok=None)
        sums: dict[str, Decimal] = {}
        for profile in profiles:
            for price, volume in profile.items(): sums[str(dec(price))] = sums.get(str(dec(price)), Decimal(0)) + dec(volume)
        return RecipeResult("O070", "hole", {"composite": sums, "total": sum(sums.values(), Decimal(0)),
            "automatic_window_selection": None}, ["HOLE:O070:constituent_identity"], inp.get("known_at"), True, None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O070", exc)


def o071(inp: dict) -> RecipeResult:
    try:
        lo, hi = dec(inp["lo"]), dec(inp["hi"])
        if lo > hi: raise ProfileError("dealing range bounds are reversed")
        selected, use = inp.get("selected_at"), inp.get("use_at")
        if selected is not None and use is not None and selected > use: raise ProfileError("dealing range selected after use")
        side = inp.get("thesis_side")
        control = dec(inp.get("controlling_reference", inp.get("controlling_low") if side in {None, "long"} else inp.get("controlling_high")))
        holes = [f"HOLE:O071:{key}" for key in ("band_id", "rationale", "thesis_side") if inp.get(key) is None]
        px = dec(inp.get("price"))
        return RecipeResult("O071", "computed" if not holes else "hole", {"dealing_band": [lo, hi], "width": hi-lo,
            "band_id": inp.get("band_id"), "controlling_reference": control,
            "inside": None if px is None else lo <= px <= hi,
            "band_known_before_use": None if selected is None or use is None else selected <= use,
            "parent_ids": list(inp.get("parent_ids", ())), "rationale": inp.get("rationale")}, holes,
            selected or inp.get("known_at"), True, None if holes else True)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O071", exc)


def o072(inp: dict) -> RecipeResult:
    try:
        lo, hi = dec(inp["lo"]), dec(inp["hi"])
        if lo > hi: raise ProfileError("reaction band bounds are reversed")
        band_id = inp.get("band_id")
        contact_band_id = inp.get("contact_band_id", inp.get("other_band_id", band_id))
        known, contact, use = inp.get("defense_known_at", inp.get("defended_at")), inp.get("contact_at"), inp.get("use_at")
        prior = known is not None and contact is not None and known < contact and (use is None or known <= use)
        same = band_id is not None and contact_band_id == band_id
        fresh = inp.get("fresh_defense_at")
        current = None if fresh is None else (
            False if contact is None else fresh >= contact and (use is None or fresh <= use)
        )
        history = list(inp.get("history_ids", ()))
        holes = []
        if known is None or contact is None: holes.append("HOLE:O072:history")
        if band_id is None: holes.append("HOLE:O072:band_id")
        return RecipeResult("O072", "computed" if not holes else "hole", {"band": [lo, hi],
            "prior_defense_known": prior and same, "same_band_contact": same,
            "current_defense": current, "fresh_available": current,
            "history_ids": history, "inherit_other_band": False if contact_band_id != band_id else None,
            "contact_at": contact}, holes, max((v for v in (known, fresh if current else None) if v is not None), default=None), True, None if holes else True)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O072", exc)


def o073(inp: dict) -> RecipeResult:
    try:
        profile = inp.get("profile")
        if not isinstance(profile, ProfileSnapshot):
            hold, use = inp.get("hold_known_at"), inp.get("use_at")
            if hold is not None and use is not None and hold > use: raise ProfileError("opening response is unavailable at decision")
            return RecipeResult("O073", "hole", {"lvn": inp.get("lvn"), "older_poc": dec(inp.get("older_poc")),
                "rth_poc_does_not_revise": dec(inp.get("rth_poc")), "hold_available": None if hold is None or use is None else hold <= use,
                "overnight_profile_snapshot": None}, ["HOLE:O073:overnight_profile"], inp.get("known_at"), True, None)
        if profile.kind != "overnight": raise ProfileError("O073 requires an overnight profile")
        source = inp.get("source")
        if source == "sires":
            start, end = ns_to_et(profile.formation_start), ns_to_et(profile.formation_end)
            if (start.hour, start.minute, end.hour, end.minute) != (18, 0, 9, 30) or profile.window_id.find("sires-overnight") < 0:
                raise ProfileError("Sires O073 must bind O011 18:00-09:30 ET")
        lvn = inp.get("lvn_band")
        older = inp.get("older_poc_reference")
        alignment = None
        if lvn is not None and isinstance(older, ProfileReference):
            if older.profile_id == profile.profile_id: raise ProfileError("older POC must retain a distinct earlier profile identity")
            alignment = dec(lvn[0]) <= older.price <= dec(lvn[1])
        hold = inp.get("opening_response")
        use = inp.get("use_at")
        response_available = hold is not None and hold.get("known_at") is not None and (use is None or hold["known_at"] <= use)
        landmarks = list(inp.get("landmarks", ()))
        holes = []
        if lvn is None: holes.append("HOLE:O073:lvn")
        if profile.coverage_ok is not True: holes.append("HOLE:O073:coverage")
        value = {"overnight_profile_snapshot": snapshot_payload(profile), "landmarks": landmarks,
            "lvn_band": None if lvn is None else [dec(lvn[0]), dec(lvn[1])],
            "older_poc_alignment": alignment, "older_poc_reference_id": None if older is None else older.reference_id,
            "opening_response": hold if response_available else None, "opening_response_available": response_available,
            "source_clock_id": "O011:sires_overnight_1800_0930_et" if source == "sires" else inp.get("source_clock_id")}
        return _result("O073", profile, value, holes=holes)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O073", exc)


def o074(inp: dict) -> RecipeResult:
    label = inp.get("source_inventory", inp.get("inventory"))
    if label not in {None, "net_long", "net_short", "balanced", "unknown"}:
        return _invalid("O074", ProfileError("unsupported source inventory label"))
    if label is None:
        return RecipeResult("O074", "hole", {"inventory": None, "source_inventory": None, "automatic_inventory": None}, ["HOLE:O074:source_record"], inp.get("known_at"), None, None)
    inventory_at = inp.get("inventory_known_at", inp.get("known_at"))
    response = inp.get("opening_response", inp.get("later_response"))
    response_at = response.get("known_at") if isinstance(response, Mapping) else inp.get("response_known_at")
    if response_at is not None and inventory_at is not None and response_at < inventory_at:
        return _invalid("O074", ProfileError("opening response precedes frozen inventory"))
    return RecipeResult("O074", "hole", {"inventory": label, "source_inventory": label,
        "measured_evidence": list(inp.get("measured_evidence", ())), "opening_response": response,
        "revised_by_later": False, "automatic_inventory": None,
        "profile_id": getattr(inp.get("profile"), "profile_id", None)}, ["HOLE:O074:classifier"], inventory_at, True, None)


def o075(inp: dict) -> RecipeResult:
    try:
        profile = inp.get("profile")
        if isinstance(profile, ProfileSnapshot) and profile.kind != "prior_eth": raise ProfileError("ETH identity cannot alias another profile kind")
        open_px = dec(inp.get("open_px")); balance = inp.get("balance_band", inp.get("balance")); va = inp.get("va_band", inp.get("va"))
        if isinstance(profile, ProfileSnapshot) and va is None and profile.val is not None and profile.vah is not None: va = [profile.val, profile.vah]
        inside_balance = None if balance is None or open_px is None else dec(balance[0]) <= open_px <= dec(balance[1])
        inside_va = None if va is None or open_px is None else dec(va[0]) <= open_px <= dec(va[1])
        scope_resolved = inp.get("scope_resolved", not inp.get("condition_unresolved", True)) is True
        holes = [] if scope_resolved else ["HOLE:O075:scope"]
        if profile is None: holes.append("HOLE:O075:profile")
        value = {"eth_profile_id": None if profile is None else profile.profile_id,
            "snapshot_id": None if profile is None else profile.snapshot_id,
            "scope_resolved": scope_resolved, "balance_band": balance, "va_band": va,
            "inside_balance": inside_balance, "inside_va": inside_va,
            "cohort_eligibility": inside_balance if scope_resolved else None,
            "scope_holes": holes, "literal_source_label": inp.get("literal_source_label")}
        known_at = profile.known_at if isinstance(profile, ProfileSnapshot) else inp.get("known_at")
        return RecipeResult("O075", "computed" if not holes else "hole", value, holes, known_at, True, True if isinstance(profile, ProfileSnapshot) and profile.coverage_ok is True and not holes else None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O075", exc)


def o076(inp: dict) -> RecipeResult:
    try:
        profile = inp.get("profile")
        H = profile.H if isinstance(profile, ProfileSnapshot) else dec(inp.get("H")); L = profile.L if isinstance(profile, ProfileSnapshot) else dec(inp.get("L"))
        if H is None or L is None or H < L: raise ProfileError("verified profile H/L are required")
        mpoc = (H + L) / 2; volume_poc = profile.poc if isinstance(profile, ProfileSnapshot) else dec(inp.get("volume_poc")); price = dec(inp.get("price"))
        return RecipeResult("O076", "computed", {"mpoc": mpoc, "profile_id": None if profile is None else profile.profile_id,
            "snapshot_id": None if profile is None else profile.snapshot_id, "volume_poc": volume_poc,
            "touch_mpoc": None if price is None else price == mpoc,
            "touch_vpoc": None if price is None or volume_poc is None else price == volume_poc,
            "distinct": volume_poc is None or mpoc != volume_poc,
            "opening_condition": inp.get("opening_condition"), "later_contact": inp.get("later_contact")},
            [], profile.known_at if isinstance(profile, ProfileSnapshot) else inp.get("known_at"), True,
            profile.coverage_ok if isinstance(profile, ProfileSnapshot) else True)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O076", exc)


def o077(inp: dict) -> RecipeResult:
    try:
        if "profile_definition" in inp or isinstance(inp.get("profile"), ProfileSnapshot):
            profile = _profile_input(inp)
            rows = [asdict(row) for row in profile.rows]
            buy = {str(row.price): row.buy_volume for row in profile.rows}; sell = {str(row.price): row.sell_volume for row in profile.rows}
            unknown = {str(row.price): row.unknown_volume for row in profile.rows}; totals = {str(row.price): row.total_volume for row in profile.rows}
            delta = {str(row.price): row.full_delta for row in profile.rows}; known_delta = sum((row.known_delta for row in profile.rows), Decimal(0)); unknown_total = sum((row.unknown_volume for row in profile.rows), Decimal(0))
            value = {"profile_id": profile.profile_id, "snapshot_id": profile.snapshot_id,
                "as_of": profile.as_of, "rows": rows, "buy_by_price": buy, "sell_by_price": sell,
                "unknown_by_price": unknown, "total_by_price": totals, "delta_by_price": delta,
                "known_window_delta": known_delta, "window_delta": known_delta if unknown_total == 0 else None,
                "known_delta": known_delta if unknown_total == 0 else None,
                "delta_interval": [known_delta-unknown_total, known_delta+unknown_total],
                "total": profile.total_volume, "total_volume": profile.total_volume,
                "aggressor_convention": "B_buy_A_sell_N_unknown"}
            return _result("O077", profile, value)
        levels = inp.get("levels", ()); known_delta = Decimal(0); total = Decimal(0); unknown = Decimal(0); rows=[]
        for index, level in enumerate(levels):
            b, a, n = dec(level.get("B", 0)), dec(level.get("A", 0)), dec(level.get("N", 0)); kd=b-a
            price = dec(level.get("price", index)); rows.append({"price": price, "buy_volume": b, "sell_volume": a, "unknown_volume": n, "total_volume": b+a+n, "known_delta": kd, "full_delta": kd if n == 0 else None, "delta_low": kd-n, "delta_high": kd+n})
            known_delta += kd; total += b+a+n; unknown += n
        return RecipeResult("O077", "hole", {"rows": rows,
            "buy_by_price": {str(r['price']):r['buy_volume'] for r in rows}, "sell_by_price": {str(r['price']):r['sell_volume'] for r in rows},
            "unknown_by_price": {str(r['price']):r['unknown_volume'] for r in rows}, "total_by_price": {str(r['price']):r['total_volume'] for r in rows},
            "delta_by_price": {str(r['price']):r['full_delta'] for r in rows}, "known_window_delta": known_delta,
            "window_delta": known_delta if unknown == 0 else None, "known_delta": known_delta if unknown == 0 else None,
            "delta_interval": [known_delta-unknown, known_delta+unknown], "total": total,
            "aggressor_convention": "B_buy_A_sell_N_unknown"}, ["HOLE:O077:profile_definition"], inp.get("known_at"), True, None)
    except (ProfileError, KeyError, TypeError, ValueError) as exc: return _invalid("O077", exc)


REGISTRATION_OVERRIDES = {
    "O061": o061, "O062": o062, "O063": o063, "O064": o064,
    "O065": o065, "O066": o066, "O067": o067, "O068": o068,
    "O069": o069, "O070": o070, "O071": o071, "O072": o072,
    "O073": o073, "O074": o074, "O075": o075, "O076": o076,
    "O077": o077,
}


def _native_profile(recipe_id: str, config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    """Adapt Astra's ``ResolvedMembers`` boundary to the profile domain."""

    definition = config.get("profile_definition")
    if not isinstance(definition, ProfileDefinition):
        raise ProfileError(f"{recipe_id} requires a frozen ProfileDefinition setting")
    if str(definition.instrument.instrument_id) != str(resolved.instrument_id):
        raise ProfileError("resolved instrument does not match profile definition")
    if definition.window.start != resolved.start_ns or definition.window.end != resolved.end_ns:
        raise ProfileError("resolved interval does not match the dated profile window")
    # Price alignment is an instrument fact, so the manifest/configuration may
    # describe the profile window but cannot assert its own tick.  Bind every
    # native profile to the definition selected and authenticated by the
    # resolver.  Without that record (or its availability time), the profile
    # cannot be constructed causally and must remain explicitly invalid.
    native = getattr(resolved, "instrument_definition", None)
    if native is None:
        return _invalid(recipe_id, ProfileError("trusted native instrument definition is unavailable"))
    if str(native.instrument_id) != str(resolved.instrument_id):
        return _invalid(recipe_id, ProfileError("native instrument definition identity mismatch"))
    if native.known_at is None:
        return _invalid(recipe_id, ProfileError("native instrument definition availability is unknown"))
    trusted_instrument = InstrumentDefinition(
        definition_id=native.definition_id,
        instrument_id=native.instrument_id,
        tick_size=native.tick_size,
        known_at=native.known_at,
    )
    definition = replace(definition, instrument=trusted_instrument)

    state = "complete" if resolved.coverage_ok is True else "unavailable"
    holes = () if state == "complete" else (f"HOLE:{recipe_id}:coverage",)
    coverage = Coverage(state, resolved.start_ns, resolved.end_ns, holes,
                        coverage_id=f"resolved:{definition.window.window_id}")
    as_of = config.get("as_of", resolved.end_ns)
    profile = build_profile(definition, resolved.rows(), as_of=as_of, coverage=coverage)
    if recipe_id == "O061":
        return _result("O061", profile)
    if recipe_id == "O063":
        if profile.kind != "developing_rth":
            raise ProfileError("O063 requires a developing_rth profile definition")
        return _result("O063", profile)
    if recipe_id == "O077":
        return o077({"profile": profile})
    raise ProfileError(f"unsupported native profile producer {recipe_id}")


def native_o061(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return _native_profile("O061", config, resolved)


def native_o063(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return _native_profile("O063", config, resolved)


def native_o077(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return _native_profile("O077", config, resolved)


NATIVE_PRODUCERS = {"O061": native_o061, "O063": native_o063, "O077": native_o077}


_PROFILE_OUTPUT_SCHEMA = {
    "snapshot_id": OutputField((str,)), "profile_id": OutputField((str,)),
    "kind": OutputField((str,)), "instrument_id": OutputField((str, int)),
    "instrument_definition_id": OutputField((str,)), "tick_size": OutputField((Decimal,)),
    "session_date": OutputField((str,), True), "window_id": OutputField((str,)),
    "formation_start": OutputField((int,)), "formation_end": OutputField((int,)),
    "as_of": OutputField((int,)), "known_at": OutputField((int,)),
    "rows": OutputField((list,)), "volume_histogram": OutputField((dict,)),
    "native_volume_by_price": OutputField((dict,)), "source_bins": OutputField((list,)),
    "total": OutputField((Decimal,)), "total_volume": OutputField((Decimal,)),
    "H": OutputField((Decimal,), True), "L": OutputField((Decimal,), True),
    "poc": OutputField((Decimal,), True), "poc_candidates": OutputField((list,)),
    "poc_tie_state": OutputField((str,)), "val": OutputField((Decimal,), True),
    "vah": OutputField((Decimal,), True), "value_area_fraction": OutputField((Decimal,), True),
    "value_area_config_id": OutputField((str,), True),
    "value_area_algorithm": OutputField((str,), True),
    "value_area_tie_policy": OutputField((str,), True),
    "volume_inside_value": OutputField((Decimal,), True),
    "achieved_value_fraction": OutputField((Decimal,), True),
    "coverage": OutputField((dict,)), "coverage_ok": OutputField((bool,), True),
    "event_ids": OutputField((list,)), "parent_ids": OutputField((list,)),
    "source_id": OutputField((str,), True), "selection_rationale": OutputField((str,), True),
    "bin_width": OutputField((Decimal,), True),
    "bin_origin": OutputField((Decimal,), True), "bin_membership": OutputField((str,), True),
}

OUTPUT_SCHEMAS = {
    "O061": dict(_PROFILE_OUTPUT_SCHEMA),
    "O063": dict(_PROFILE_OUTPUT_SCHEMA),
    "O077": {
        "profile_id": OutputField((str,)), "snapshot_id": OutputField((str,)),
        "as_of": OutputField((int,)), "rows": OutputField((list,)),
        "buy_by_price": OutputField((dict,)), "sell_by_price": OutputField((dict,)),
        "unknown_by_price": OutputField((dict,)), "total_by_price": OutputField((dict,)),
        "delta_by_price": OutputField((dict,)), "known_window_delta": OutputField((Decimal,)),
        "window_delta": OutputField((Decimal,), True), "known_delta": OutputField((Decimal,), True),
        "delta_interval": OutputField((list,)), "total": OutputField((Decimal,)),
        "total_volume": OutputField((Decimal,)), "aggressor_convention": OutputField((str,)),
    },
}


__all__ = [
    "Coverage", "InstrumentDefinition", "PriceRow", "ProfileDefinition",
    "ProfileError", "ProfileReference", "ProfileSnapshot", "ProfileWindow",
    "NATIVE_PRODUCERS", "OUTPUT_SCHEMAS", "REGISTRATION_OVERRIDES",
    "SOURCE_VALUE_AREA_CONFIGS", "ValueAreaConfig",
    "build_profile", "compose_profiles", "sires_overnight_window",
    "snapshot_payload",
]
