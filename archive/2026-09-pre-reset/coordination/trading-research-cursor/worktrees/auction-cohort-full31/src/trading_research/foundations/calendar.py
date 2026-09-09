"""Versioned explicit calendar rows; no inferred holidays or silent DST coercion."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.time import datetime_ns, timestamp
from trading_research.operations.artifacts import digest


def _date(value):
    if type(value) is not date:
        raise ContractError('calendar dates must be civil dates, without a time component')


def _label(value):
    if type(value) is not str or not value.strip() or value.strip() != value:
        raise ContractError('calendar names and versions must be explicit strings')


def local_timestamp(day: date, wall: time, zone: str, *, fold: int | None = None) -> int:
    _date(day)
    _label(zone)
    if (type(wall) is not time or wall.tzinfo is not None
            or fold is not None and (type(fold) is not int or fold not in (0, 1))):
        raise ContractError("declare the zone and any repeated-wall-time fold explicitly")
    naive = datetime.combine(day, wall)
    try:
        tz = ZoneInfo.no_cache(zone)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise ContractError('unknown or invalid explicit timezone') from exc
    candidates = {}
    for choice in (0, 1):
        aware = naive.replace(tzinfo=tz, fold=choice)
        round_trip = aware.astimezone(timezone.utc).astimezone(tz)
        if round_trip.replace(tzinfo=None) == naive and round_trip.fold == choice:
            candidates[choice] = datetime_ns(aware)
    if not candidates:
        raise ContractError("nonexistent local wall time during a DST transition")
    if fold is not None:
        if fold not in candidates:
            raise ContractError("declared fold does not identify a valid wall time")
        return candidates[fold]
    if len(set(candidates.values())) > 1:
        raise ContractError("ambiguous repeated local time requires an explicit fold")
    return next(iter(candidates.values()))


@dataclass(frozen=True)
class FormationWindow:
    id: str
    trading_date: date
    start: int
    end: int
    clock_variant: str
    definition_version: str

    def __post_init__(self) -> None:
        _date(self.trading_date)
        for value in (self.id, self.clock_variant, self.definition_version):
            _label(value)
        timestamp(self.start)
        timestamp(self.end)
        if self.end <= self.start:
            raise ContractError("formation windows require positive half-open intervals and source versions")

    def contains(self, at: int) -> bool:
        return self.start <= timestamp(at) < self.end


def wall_window(*, id: str, trading_date: date, start_day: date, start: time, end: time,
                zone: str, definition_version: str, crosses_midnight: bool = False,
                start_fold: int | None = None, end_fold: int | None = None) -> FormationWindow:
    _date(trading_date)
    _date(start_day)
    if type(crosses_midnight) is not bool:
        raise ContractError("cross-midnight attribution must be explicit")
    end_day = start_day + timedelta(days=1) if crosses_midnight else start_day
    return FormationWindow(id, trading_date, local_timestamp(start_day, start, zone, fold=start_fold),
                           local_timestamp(end_day, end, zone, fold=end_fold), zone, definition_version)


@dataclass(frozen=True)
class Session:
    id: str
    trading_date: date
    instrument_root: str
    open_at: int
    close_at: int
    required_boundaries: tuple[tuple[str, int], ...]
    execution_margin_ns: int
    known_at: int
    source_version: str
    timezone_version: str
    eligible: bool
    eligibility_reason: str

    def __post_init__(self) -> None:
        _date(self.trading_date)
        for value in (self.id, self.instrument_root, self.source_version, self.timezone_version, self.eligibility_reason):
            _label(value)
        if (type(self.required_boundaries) is not tuple
                or any(type(p) is not tuple or len(p) != 2 for p in self.required_boundaries)
                or type(self.eligible) is not bool):
            raise ContractError('calendar boundaries and eligibility must be typed immutable facts')
        for name, _ in self.required_boundaries:
            _label(name)
        for at in (self.open_at, self.close_at, self.known_at, *(t for _, t in self.required_boundaries)):
            timestamp(at)
        timestamp(self.execution_margin_ns)
        if self.close_at <= self.open_at or self.execution_margin_ns < 0:
            raise ContractError("calendar row lacks explicit version/eligibility/boundary terms")
        names = [name for name, _ in self.required_boundaries]
        if len(set(names)) != len(names) or any(not name or not self.open_at < t <= self.close_at for name, t in self.required_boundaries):
            raise ContractError("conflicting or out-of-session required boundary")
        if timestamp(self.flatten_at) <= self.open_at:
            raise ContractError("execution margin consumes the entire session")

    @property
    def flatten_at(self) -> int:
        return min([self.close_at, *(t for _, t in self.required_boundaries)]) - self.execution_margin_ns

    @property
    def version(self) -> str:
        return digest(self)


class Calendar:
    def __init__(self):
        self._versions: dict[str, Session] = {}

    def append(self, session: Session) -> None:
        if type(session) is not Session:
            raise ContractError('calendar append requires a typed immutable session')
        key = (session.trading_date, session.instrument_root)
        for old in self._versions.values():
            same_key = (old.trading_date, old.instrument_root) == key
            if (old.id == session.id) != same_key:
                raise ContractError('calendar logical ID must retain one trading-date/instrument identity')
        self._versions[session.version] = session

    def resolve(self, trading_date: date, instrument_root: str, *, cut: int) -> Session:
        _date(trading_date)
        _label(instrument_root)
        timestamp(cut)
        rows = [s for s in self._versions.values() if s.trading_date == trading_date
                and s.instrument_root == instrument_root and s.known_at <= cut]
        if not rows:
            raise DependencyUnavailable("calendar or required flatten boundary was not known at this cut")
        newest = max(s.known_at for s in rows)
        rows = [s for s in rows if s.known_at == newest]
        if len(rows) != 1:
            raise ContractError("conflicting calendar sources at the same publication cut")
        return rows[0]

    def timers(self, trading_date: date, instrument_root: str, *, cut: int) -> tuple[tuple[int, str], ...]:
        s = self.resolve(trading_date, instrument_root, cut=cut)
        # Boundary actions are scheduled even if the market stream has no next tick.
        return tuple(sorted(((s.open_at, "session_open"), (s.flatten_at, "flatten_deadline"),
                             (s.close_at, "session_close"))))
