"""C02 clock and bar primitives used by the method pack.

The method pack stores event keys as signed UTC nanoseconds, while source
clocks are expressed as ET wall time.  This module deliberately keeps those
two representations visible: converting a wall clock to UTC is a dated
operation and all intervals are half open.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Any, Mapping, Sequence, Iterable
from zoneinfo import ZoneInfo

from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.time import datetime_ns
from trading_research.research.method_pack.logic import dec

ET = "America/New_York"
_ET_ZONE = ZoneInfo.no_cache(ET)
NS = 1_000_000_000
MS_NS = 1_000_000
MINUTE_NS = 60 * NS
I64_MIN = -(2**63)
I64_MAX = 2**63 - 1


def _ns(value: Any) -> int:
    """Validate and return a UTC nanosecond key without float conversion."""

    if type(value) is not int or not I64_MIN <= value <= I64_MAX:
        raise ValueError("event keys must be signed int64 UTC nanoseconds")
    return value


def _valid_wall_candidates(day: date, wall: time) -> list[tuple[int, int]]:
    """Return valid UTC keys for a wall time, including both DST folds."""

    naive = datetime.combine(day, wall)
    result: dict[int, int] = {}
    for fold in (0, 1):
        aware = naive.replace(tzinfo=_ET_ZONE, fold=fold)
        round_trip = aware.astimezone(timezone.utc).astimezone(_ET_ZONE)
        if round_trip.replace(tzinfo=None) == naive and round_trip.fold == fold:
            result[datetime_ns(aware)] = fold
    return sorted((key, fold) for key, fold in result.items())


def et_ns(
    day: date,
    hour: int,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    *,
    nanosecond: int = 0,
    fold: int | None = None,
) -> int:
    """Convert a dated America/New_York wall clock to UTC nanoseconds."""

    if type(day) is not date:
        raise ValueError("day must be a civil date")
    if type(nanosecond) is not int or not 0 <= nanosecond < 1_000:
        raise ValueError("nanosecond must be in [0, 1000)")
    wall = time(hour, minute, second, microsecond)
    return _ns(local_timestamp(day, wall, ET, fold=fold) + nanosecond)


def utc_datetime_ns(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    *,
    nanosecond: int = 0,
) -> int:
    """Build an exact UTC nanosecond key from calendar fields."""

    if type(nanosecond) is not int or not 0 <= nanosecond < 1_000:
        raise ValueError("nanosecond must be in [0, 1000)")
    base = datetime_ns(
        datetime(
            year,
            month,
            day,
            hour,
            minute,
            second,
            microsecond,
            tzinfo=timezone.utc,
        )
    )
    return _ns(base + nanosecond)


def ns_to_et(ns: int) -> datetime:
    """Return an ET datetime without converting the key through a float."""

    value = _ns(ns)
    seconds, nanos = divmod(value, NS)
    utc = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(
        microsecond=nanos // 1_000
    )
    return utc.astimezone(_ET_ZONE)


def ns_to_et_parts(ns: int) -> dict[str, Any]:
    """Return ET date/clock fields and the exact sub-microsecond remainder."""

    value = _ns(ns)
    seconds, nanos = divmod(value, NS)
    local = datetime.fromtimestamp(seconds, tz=timezone.utc).astimezone(_ET_ZONE)
    local = local.replace(microsecond=nanos // 1_000)
    return {
        "datetime": local,
        "date": local.date(),
        "time": local.timetz().replace(tzinfo=None),
        "fold": local.fold,
        "nanosecond": nanos % 1_000,
        "event_ns": value,
        "zone": ET,
    }


def session_date_et(ns: int) -> date:
    return ns_to_et(ns).date()


def aligned_bar_start(event_ns: int, size_minutes: int, day: date | None = None) -> int:
    """Return the ET-wall-clock aligned start containing ``event_ns``.

    ``day`` is retained for compatibility with the original helper.  When it
    is supplied it must be the event's ET date; silently using a different
    date would create a cross-session join.
    """

    event_ns = _ns(event_ns)
    if type(size_minutes) is not int or not 0 < size_minutes <= 24 * 60:
        raise ValueError("size_minutes must be an integer in [1, 1440]")
    local = ns_to_et(event_ns)
    event_day = local.date()
    if day is not None:
        if type(day) is not date:
            raise ValueError("day must be a civil date")
        if day != event_day:
            raise ValueError("alignment day does not match event ET date")
    minute = local.hour * 60 + local.minute
    bucket = (minute // size_minutes) * size_minutes
    candidates = _valid_wall_candidates(
        event_day, time(bucket // 60, bucket % 60)
    )
    if not candidates:
        raise ValueError("event falls in a nonexistent ET clock bucket")
    if len(candidates) == 1:
        return candidates[0][0]
    for key, candidate_fold in candidates:
        if candidate_fold == local.fold:
            return key
    raise ValueError("could not retain the event's DST fold")


def aligned_bar_bounds(event_ns: int, size_minutes: int) -> tuple[int, int]:
    """Return the half-open ET-aligned interval containing an event."""

    start = aligned_bar_start(event_ns, size_minutes)
    local = ns_to_et(start)
    minute = local.hour * 60 + local.minute + size_minutes
    end_day, end_minute = divmod(minute, 24 * 60)
    end_date = local.date() + timedelta(days=end_day)
    end_wall = time(end_minute // 60, end_minute % 60)
    candidates = _valid_wall_candidates(end_date, end_wall)
    if not candidates:
        raise ValueError("bar end is a nonexistent ET wall-clock time")
    ends = [key for key, _fold in candidates if key > start]
    if not ends:
        raise ValueError("bar end does not follow bar start")
    return start, min(ends)


def _clock_bucket_starts(start_ns: int, end_ns: int, size_minutes: int = 1) -> list[int]:
    """Enumerate ET wall-clock multiples in a half-open UTC interval."""

    start_ns, end_ns = _ns(start_ns), _ns(end_ns)
    if end_ns < start_ns:
        raise ValueError("clock interval end precedes start")
    if type(size_minutes) is not int or not 0 < size_minutes <= 24 * 60:
        raise ValueError("size_minutes must be an integer in [1, 1440]")
    start_day = ns_to_et(start_ns).date() - timedelta(days=1)
    end_day = ns_to_et(end_ns).date() + timedelta(days=1)
    out: list[int] = []
    day = start_day
    while day <= end_day:
        for minute in range(0, 24 * 60, size_minutes):
            for key, _fold in _valid_wall_candidates(
                day, time(minute // 60, minute % 60)
            ):
                if start_ns <= key < end_ns:
                    out.append(key)
        day += timedelta(days=1)
    return sorted(set(out))


def minute_starts(start_ns: int, end_ns: int) -> list[int]:
    """Return ET-aligned one-minute starts in ``[start_ns, end_ns)``."""

    return _clock_bucket_starts(start_ns, end_ns, 1)


def clock_window(
    day: date,
    start: time,
    end: time,
    *,
    source_version: str = "",
    clock_id: str = "",
    crosses_midnight: bool = False,
    start_fold: int | None = None,
    end_fold: int | None = None,
    verified: bool | None = True,
) -> dict[str, Any]:
    """Construct a dated source clock and retain its verification state."""

    if type(day) is not date or type(start) is not time or type(end) is not time:
        raise ValueError("clock windows require a date and naive wall times")
    if start.tzinfo is not None or end.tzinfo is not None:
        raise ValueError("source clock wall times must not carry a second zone")
    end_day = day + timedelta(days=1) if crosses_midnight else day
    start_ns = local_timestamp(day, start, ET, fold=start_fold)
    end_ns = local_timestamp(end_day, end, ET, fold=end_fold)
    if end_ns <= start_ns:
        raise ValueError("clock windows require a positive half-open interval")
    return {
        "clock_id": clock_id,
        "source_version": source_version,
        "session_date_et": day,
        "start_et": start,
        "end_et": end,
        "start_ns": start_ns,
        "end_ns": end_ns,
        "bar_close_at": end_ns,
        "window_known_at": end_ns,
        "crosses_midnight": crosses_midnight,
        "clock_verified": verified,
        "zone": ET,
    }


@dataclass(frozen=True)
class Bar:
    """Immutable normalized time bar."""

    bar_id: str
    instrument_id: str
    kind: str
    size: str
    start: int
    end: int
    O: Decimal | None
    H: Decimal | None
    L: Decimal | None
    C: Decimal | None
    volume: Decimal
    complete: bool
    coverage_state: str
    known_at: int | None
    native_source_compatible: bool | None = True
    member_count: int = 0
    member_event_ids: tuple[str, ...] = field(default_factory=tuple)
    source_precision: str = ""
    ordering_basis: str = ""

    @property
    def V(self) -> Decimal:
        return self.volume


def _field(row: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in row:
            return row[name]
    return None


def _member_bounds(row: Mapping[str, Any]) -> tuple[int | None, int | None]:
    start = _field(row, "start", "start_ns", "bar_start_ns")
    end = _field(row, "end", "end_ns", "bar_end_ns")
    if start is None and _field(row, "event_ns", "t") is not None:
        start = _field(row, "event_ns", "t")
        end = start + 1
    return (
        None if start is None else _ns(start),
        None if end is None else _ns(end),
    )


def _ordered_members(members: Sequence[Mapping[str, Any]]) -> tuple[list[Mapping[str, Any]], str]:
    """Order distinct intervals while preserving unresolved timestamp ties."""

    rows = list(members)
    if len(rows) < 2:
        return rows, "single_or_source_order"
    bounds = [_member_bounds(row) for row in rows]
    if any(start is None for start, _ in bounds):
        return rows, "source_order_unverified"
    starts = [start for start, _ in bounds]
    if len(starts) != len(set(starts)):
        return rows, "unknown_order"
    return [
        row for _, row in sorted(zip(starts, rows), key=lambda item: item[0])
    ], "timestamp_order"


def aggregate_ohlcv(members: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate complete finer bars/events with exact decimal prices."""

    if not members:
        return {
            "O": None,
            "H": None,
            "L": None,
            "C": None,
            "V": Decimal(0),
            "volume": Decimal(0),
            "empty": True,
            "complete": False,
            "missing_fields": [],
            "ordering_basis": "empty",
        }
    ordered, ordering_basis = _ordered_members(members)
    missing: list[str] = []
    values: dict[str, list[Decimal | None]] = {key: [] for key in ("O", "H", "L", "C")}
    volumes: list[Decimal] = []
    aliases = {
        "O": ("O", "o", "open", "price_open"),
        "H": ("H", "h", "high", "price_high"),
        "L": ("L", "l", "low", "price_low"),
        "C": ("C", "c", "close", "price_close"),
    }
    for row in ordered:
        for key, names in aliases.items():
            value = _field(row, *names)
            values[key].append(None if value is None else dec(value))
            if value is None and key not in missing:
                missing.append(key)
        raw_volume = _field(row, "V", "v", "volume", "size")
        if raw_volume is None:
            if "V" not in missing:
                missing.append("V")
        else:
            volumes.append(dec(raw_volume) or Decimal(0))
        if row.get("complete") is False and "complete" not in missing:
            missing.append("complete")
    volume = sum(volumes, Decimal(0))
    if missing:
        return {
            "O": None,
            "H": None,
            "L": None,
            "C": None,
            "V": volume,
            "volume": volume,
            "empty": False,
            "complete": False,
            "missing_fields": missing,
            "ordering_basis": ordering_basis,
        }
    return {
        "O": values["O"][0],
        "H": max(values["H"]),
        "L": min(values["L"]),
        "C": values["C"][-1],
        "V": volume,
        "volume": volume,
        "empty": False,
        "complete": True,
        "missing_fields": [],
        "ordering_basis": ordering_basis,
    }


def _empty_bar(
    *,
    bar_id: str,
    instrument_id: str,
    size: str,
    start_ns: int,
    end_ns: int,
    coverage_state: str,
    complete: bool,
    known_at: int | None,
    member_count: int,
) -> Bar:
    return Bar(
        bar_id=bar_id,
        instrument_id=str(instrument_id),
        kind="time",
        size=size,
        start=start_ns,
        end=end_ns,
        O=None,
        H=None,
        L=None,
        C=None,
        volume=Decimal(0),
        complete=complete,
        coverage_state=coverage_state,
        known_at=known_at,
        native_source_compatible=True,
        member_count=member_count,
    )


def time_bar_from_minutes(
    start_ns: int,
    end_ns: int,
    minute_bars: Mapping[int, Mapping[str, Any]],
    *,
    instrument_id: str,
    bar_id: str,
    size: str,
    known_empty: Iterable[int] = (),
) -> Bar:
    """Aggregate ET-aligned one-minute bars into a complete time bar."""

    start_ns, end_ns = _ns(start_ns), _ns(end_ns)
    if end_ns <= start_ns:
        raise ValueError("bar interval must be positive")
    expected = minute_starts(start_ns, end_ns)
    available = {_ns(key): value for key, value in minute_bars.items()}
    empty_keys = {_ns(key) for key in known_empty}
    missing = [key for key in expected if key not in available and key not in empty_keys]
    incomplete = [
        key
        for key in expected
        if key in available and available[key].get("complete") is False
    ]
    present = [available[key] for key in expected if key in available]
    if missing:
        return _empty_bar(
            bar_id=bar_id,
            instrument_id=str(instrument_id),
            size=size,
            start_ns=start_ns,
            end_ns=end_ns,
            coverage_state="missing_interval",
            complete=False,
            known_at=None,
            member_count=len(present),
        )
    if incomplete:
        return _empty_bar(
            bar_id=bar_id,
            instrument_id=str(instrument_id),
            size=size,
            start_ns=start_ns,
            end_ns=end_ns,
            coverage_state="incomplete_member",
            complete=False,
            known_at=None,
            member_count=len(present),
        )
    agg = aggregate_ohlcv(present)
    if not agg["complete"] and present:
        return _empty_bar(
            bar_id=bar_id,
            instrument_id=str(instrument_id),
            size=size,
            start_ns=start_ns,
            end_ns=end_ns,
            coverage_state="invalid_member",
            complete=False,
            known_at=None,
            member_count=len(present),
        )
    state = "known_empty" if not present else (
        "complete_with_empty" if empty_keys.intersection(expected) else "complete"
    )
    return Bar(
        bar_id=bar_id,
        instrument_id=str(instrument_id),
        kind="time",
        size=size,
        start=start_ns,
        end=end_ns,
        O=agg["O"],
        H=agg["H"],
        L=agg["L"],
        C=agg["C"],
        volume=agg["V"],
        complete=True,
        coverage_state=state,
        known_at=end_ns,
        native_source_compatible=True,
        member_count=len(present),
        ordering_basis=agg.get("ordering_basis", ""),
    )


def _range_member_values(row: Mapping[str, Any], start_ns: int, end_ns: int) -> tuple[bool, Decimal | None, Decimal | None]:
    """Return (inside, high, low) for a bar or a point event."""

    event = _field(row, "event_ns", "event_at")
    if event is not None:
        at = _ns(event)
        if not start_ns <= at < end_ns:
            return False, None, None
        price = _field(row, "price", "C", "c")
        value = None if price is None else dec(price)
        return True, value, value
    member_start, member_end = _member_bounds(row)
    if member_start is None:
        return False, None, None
    if member_start >= end_ns:
        return False, None, None
    if member_end is None or member_end > end_ns or member_start < start_ns:
        raise ValueError("member bar crosses the selected half-open range")
    high = _field(row, "H", "h", "high")
    low = _field(row, "L", "l", "low")
    return True, None if high is None else dec(high), None if low is None else dec(low)


def range_hl(members: Sequence[Mapping[str, Any]], start_ns: int, end_ns: int, use_at: int) -> dict[str, Any]:
    """Freeze H/L for ``[start_ns, end_ns)`` only at its end."""

    start_ns, end_ns, use_at = _ns(start_ns), _ns(end_ns), _ns(use_at)
    unavailable = {
        "available": False,
        "H": None,
        "L": None,
        "W": None,
        "known_at": None,
        "range_frozen": False,
    }
    if end_ns <= start_ns:
        return {**unavailable, "invalid": "non_positive_interval"}
    if use_at < end_ns:
        return {**unavailable, "invalid": "pre_end_use"}
    included: list[tuple[Decimal, Decimal]] = []
    for row in members:
        if row.get("complete") is False or str(row.get("coverage_state", "")).startswith("missing"):
            return {**unavailable, "invalid": "incomplete_or_missing_member"}
        try:
            inside, high, low = _range_member_values(row, start_ns, end_ns)
        except ValueError as exc:
            return {**unavailable, "invalid": str(exc)}
        if not inside:
            continue
        if high is None or low is None:
            return {**unavailable, "invalid": "missing_price"}
        included.append((high, low))
    if not included:
        return {**unavailable, "invalid": "empty_or_incomplete"}
    high = max(value[0] for value in included)
    low = min(value[1] for value in included)
    width = high - low
    if width <= 0:
        return {
            **unavailable,
            "H": high,
            "L": low,
            "W": width,
            "known_at": end_ns,
            "invalid": "non_positive_width",
        }
    return {
        "available": True,
        "H": high,
        "L": low,
        "W": width,
        "known_at": end_ns,
        "range_frozen": True,
    }


def tie_batches(events: Sequence[Mapping[str, Any]], *, timestamp_key: str = "event_ns") -> list[dict[str, Any]]:
    """Group events by timestamp without inventing order inside a tie."""

    groups: dict[int, list[Mapping[str, Any]]] = {}
    for event in events:
        raw = event.get(timestamp_key, event.get("t"))
        if raw is None:
            raise ValueError("events need a UTC nanosecond timestamp")
        groups.setdefault(_ns(raw), []).append(event)
    return [
        {
            "event_ns": at,
            "events": tuple(group),
            "ordering": "unique_timestamp" if len(group) == 1 else "unknown_order",
            "strict_order_available": len(group) == 1,
        }
        for at, group in sorted(groups.items())
    ]


def strict_order_available(
    events: Sequence[Mapping[str, Any]],
    *,
    sequence_keys: Sequence[str] = ("exchange_sequence", "sequence", "seq"),
) -> bool:
    """Whether events have a verified strict order at every timestamp."""

    for batch in tie_batches(events):
        if len(batch["events"]) == 1:
            continue
        keys = []
        for event in batch["events"]:
            value = next(
                (event.get(key) for key in sequence_keys if event.get(key) is not None),
                None,
            )
            if value is None:
                return False
            keys.append(value)
        if len(set(keys)) != len(keys):
            return False
    return True


def c02_f1() -> dict[str, Any]:
    """Synthetic C02-F1 values; no acquired data is read."""

    day_winter = date(2026, 1, 15)
    day_summer = date(2026, 7, 15)
    winter = et_ns(day_winter, 9, 30)
    summer = et_ns(day_summer, 9, 30)
    winter_utc = utc_datetime_ns(2026, 1, 15, 14, 30)
    summer_utc = utc_datetime_ns(2026, 7, 15, 13, 30)
    start = et_ns(day_winter, 9, 0)
    end = et_ns(day_winter, 10, 0)
    members = [
        {
            "start": et_ns(day_winter, 9, 10),
            "end": et_ns(day_winter, 9, 11),
            "H": Decimal("100"),
            "L": Decimal("100"),
            "O": Decimal("100"),
            "C": Decimal("100"),
            "V": Decimal(1),
        },
        {
            "start": et_ns(day_winter, 9, 59),
            "end": et_ns(day_winter, 10, 0),
            "H": Decimal("105"),
            "L": Decimal("104"),
            "O": Decimal("104"),
            "C": Decimal("105"),
            "V": Decimal(1),
        },
    ]
    at_0945 = range_hl(members, start, end, et_ns(day_winter, 9, 45))
    at_1000 = range_hl(members, start, end, end)
    later = members + [
        {
            "start": et_ns(day_winter, 10, 0),
            "end": et_ns(day_winter, 10, 1),
            "H": Decimal("120"),
            "L": Decimal("110"),
            "O": Decimal("110"),
            "C": Decimal("120"),
            "V": Decimal(1),
        }
    ]
    after_1000_bar = range_hl(later, start, end, et_ns(day_winter, 10, 1))
    five_start = et_ns(day_winter, 10, 0)
    five_end = et_ns(day_winter, 10, 5)
    minutes = {
        et_ns(day_winter, 10, 0): {"O": 1, "H": 1, "L": 1, "C": 1, "V": 1},
        et_ns(day_winter, 10, 1): {"O": 1, "H": 1, "L": 1, "C": 1, "V": 1},
        et_ns(day_winter, 10, 3): {"O": 1, "H": 1, "L": 1, "C": 1, "V": 1},
        et_ns(day_winter, 10, 4): {"O": 1, "H": 1, "L": 1, "C": 1, "V": 1},
    }
    incomplete = time_bar_from_minutes(
        five_start,
        five_end,
        minutes,
        instrument_id="NQ",
        bar_id="fivemin-gap",
        size="5m",
    )
    grouped_rows = time_bar_from_minutes(
        five_start,
        five_end,
        {
            **minutes,
            et_ns(day_winter, 10, 6): {"O": 1, "H": 1, "L": 1, "C": 1, "V": 1},
        },
        instrument_id="NQ",
        bar_id="grouped-rows",
        size="5m",
    )
    return {
        "winter_0930_et_ns": winter,
        "winter_1430_utc_ns": winter_utc,
        "summer_0930_et_ns": summer,
        "summer_1330_utc_ns": summer_utc,
        "range_at_0945_available": at_0945["available"],
        "range_at_1000": {"H": at_1000["H"], "L": at_1000["L"]},
        "later_1000_bar_changes_range": after_1000_bar["H"] != at_1000["H"],
        "five_minute_missing_1002_complete": incomplete.complete,
        "five_minute_missing_1002_ohlc": {
            "O": incomplete.O,
            "H": incomplete.H,
            "L": incomplete.L,
            "C": incomplete.C,
        },
        "grouping_five_available_rows_complete": grouped_rows.complete,
        "grouping_five_available_rows_ohlc": {
            "O": grouped_rows.O,
            "H": grouped_rows.H,
            "L": grouped_rows.L,
            "C": grouped_rows.C,
        },
    }
