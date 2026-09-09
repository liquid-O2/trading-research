"""Published cash RTH context, kept separate from futures venue eligibility."""

from dataclasses import dataclass
from datetime import date, time, timedelta
import json
from pathlib import Path
from types import MappingProxyType
from zoneinfo import TZPATH, ZoneInfo, ZoneInfoNotFoundError

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.calendar import _date, _label, local_timestamp
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest, file_digest


def _iso_date(value):
    if type(value) is not str:
        raise ContractError('published dates must use ISO civil-date strings')
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise ContractError('invalid published calendar date') from exc
    if result.isoformat() != value:
        raise ContractError('published dates must use YYYY-MM-DD')
    return result


def _wall(value):
    if type(value) is not str or ':' not in value:
        raise ContractError('cash calendar hours must be explicit local wall strings')
    try:
        result = time.fromisoformat(value)
    except ValueError as exc:
        raise ContractError('invalid cash-calendar wall time') from exc
    if result.tzinfo is not None:
        raise ContractError('cash-calendar timezone is declared separately')
    return result


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError('duplicate JSON source key cannot be silently overwritten')
        result[key] = value
    return result


def _freeze(value):
    if type(value) is dict:
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if type(value) is list:
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value):
    if isinstance(value, MappingProxyType):
        return {k: _thaw(v) for k, v in value.items()}
    if type(value) is tuple:
        return [_thaw(v) for v in value]
    return value


@dataclass(frozen=True)
class CashDay:
    day: date
    state: str
    open_at: int | None
    close_at: int | None
    known_at: int
    source_versions: tuple[str, ...]
    timezone_version: str
    convention_version: str
    scope: str = 'cash_equity_rth_context'

    def __post_init__(self):
        _date(self.day)
        timestamp(self.known_at)
        for value in (self.timezone_version, self.convention_version):
            _label(value)
        if type(self.state) is not str or self.state not in ('closed', 'regular', 'early_close') or self.scope != 'cash_equity_rth_context':
            raise ContractError('cash day must declare a supported state and cash-only scope')
        if type(self.source_versions) is not tuple or not self.source_versions:
            raise ContractError('cash source versions must be an immutable nonempty tuple')
        for value in self.source_versions:
            _label(value)
        if self.state == 'closed':
            if self.open_at is not None or self.close_at is not None:
                raise ContractError('closed cash date cannot expose an open interval')
        else:
            timestamp(self.open_at)
            timestamp(self.close_at)
            if self.close_at <= self.open_at:
                raise ContractError('cash interval must be positive and half-open')

    @property
    def version(self):
        return digest(self)


def zone_version(zone: str):
    _label(zone)
    if zone.startswith('/') or any(part in ('', '.', '..') for part in zone.split('/')):
        raise ContractError('timezone must be a relative IANA zone key')
    try:
        ZoneInfo.no_cache(zone)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise ContractError('unknown or invalid timezone key') from exc
    for root in TZPATH:
        path = Path(root) / zone
        if path.is_file():
            return file_digest(path)
    raise DependencyUnavailable('timezone database bytes unavailable for versioning')


@dataclass(frozen=True, init=False, eq=False)
class CashCalendar:
    _payload: object
    _version: str
    _zone: str
    _timezone_version: str
    _releases: tuple
    _overrides: tuple

    def __init__(self, path: Path):
        try:
            payload = json.loads(Path(path).read_text(), object_pairs_hook=_unique_object)
            self._validate(payload)
            object.__setattr__(self, '_zone', payload['zone'])
            object.__setattr__(self, '_timezone_version', zone_version(self.zone))
            object.__setattr__(self, '_version', digest(payload))
            object.__setattr__(self, '_payload', _freeze(payload))
            object.__setattr__(self, '_releases', tuple((self._available(r['published_date']), _freeze(r)) for r in payload['releases']))
            object.__setattr__(self, '_overrides', tuple((self._available(r['published_date']), _freeze(r)) for r in payload['overrides']))
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            if isinstance(exc, ContractError):
                raise
            raise ContractError('malformed or unsupported published cash calendar') from exc

    @staticmethod
    def _validate(payload):
        if (type(payload) is not dict or payload['schema'] != 'published-cash-rth-calendar-v1'
                or payload['market'] != 'NYSE cash equities'):
            raise ContractError('unrecognized calendar source scope')
        _label(payload['zone'])
        opened, closed = _wall(payload['regular_open']), _wall(payload['regular_close'])
        if opened >= closed:
            raise ContractError('cash RTH must form a positive same-date local interval')
        if type(payload['releases']) is not list or not payload['releases'] or type(payload['overrides']) is not list:
            raise ContractError('published releases and overrides require explicit lists')
        ids = set()
        for release in payload['releases']:
            if type(release) is not dict or type(release['years']) is not dict or not release['years']:
                raise ContractError('calendar release requires dated year tables')
            for key in ('id', 'source_url'):
                _label(release[key])
            _iso_date(release['published_date'])
            if release['id'] in ids:
                raise ContractError('duplicate calendar release identity')
            ids.add(release['id'])
            for year, days in release['years'].items():
                if type(year) is not str or len(year) != 4 or not year.isascii() or not year.isdigit():
                    raise ContractError('calendar year key must contain four ASCII digits')
                _iso_date(year + '-01-01')
                if type(days) is not dict or type(days['closed']) is not list or type(days['early']) is not dict:
                    raise ContractError('calendar year needs explicit closures and early-close clocks')
                for suffix in (*days['closed'], *days['early']):
                    if type(suffix) is not str:
                        raise ContractError('calendar day suffix must be a string')
                    _iso_date(year + '-' + suffix)
                if len(set(days['closed'])) != len(days['closed']) or set(days['closed']) & set(days['early']):
                    raise ContractError('duplicate or conflicting published calendar date')
                for suffix, at in days['early'].items():
                    if not opened < _wall(at) <= closed or _iso_date(year + '-' + suffix).weekday() >= 5:
                        raise ContractError('invalid cash early-close date or time')
        for row in payload['overrides']:
            if type(row) is not dict:
                raise ContractError('calendar override must be an explicit dated record')
            for key in ('id', 'source_url', 'reason'):
                _label(row[key])
            _iso_date(row['date'])
            _iso_date(row['published_date'])
            if row['id'] in ids or row['state'] != 'closed':
                raise ContractError('unsupported or duplicate published calendar override')
            ids.add(row['id'])

    @property
    def payload(self):
        return _thaw(self._payload)

    @property
    def version(self):
        return self._version

    @property
    def zone(self):
        return self._zone

    @property
    def timezone_version(self):
        return self._timezone_version

    @property
    def releases(self):
        return tuple((known, _thaw(row)) for known, row in self._releases)

    @property
    def overrides(self):
        return tuple((known, _thaw(row)) for known, row in self._overrides)

    def _available(self, published_date):
        return local_timestamp(_iso_date(published_date) + timedelta(days=1), time(0), self.zone)

    def resolve(self, day: date, *, cut: int):
        _date(day)
        timestamp(cut)
        if zone_version(self.zone) != self.timezone_version:
            raise DependencyUnavailable('timezone bytes changed; create a new cash calendar version')
        releases = [(known, r) for known, r in self._releases if known <= cut and str(day.year) in r['years']]
        if not releases:
            raise DependencyUnavailable('cash-calendar year not published or supplied at this cut')
        newest = max(k for k, _ in releases)
        latest = [r for k, r in releases if k == newest]
        if len(latest) != 1:
            raise ContractError('ambiguous latest cash-calendar release')
        release = latest[0]
        spec = release['years'][str(day.year)]
        suffix = day.strftime('%m-%d')
        known, sources = newest, [digest(_thaw(release))]
        state = 'closed' if day.weekday() >= 5 or suffix in spec['closed'] else ('early_close' if suffix in spec['early'] else 'regular')
        changes = [(k, r) for k, r in self._overrides if k <= cut and r['date'] == day.isoformat()]
        if changes:
            last = max(k for k, _ in changes)
            rows = [r for k, r in changes if k == last]
            if len(rows) != 1:
                raise ContractError('conflicting known calendar override')
            state, known = 'closed', max(known, last)
            sources.append(digest(_thaw(rows[0])))
        opened = closed = None
        if state != 'closed':
            opened = local_timestamp(day, _wall(self._payload['regular_open']), self.zone)
            closed = local_timestamp(day, _wall(spec['early'].get(suffix, self._payload['regular_close'])), self.zone)
        if zone_version(self.zone) != self.timezone_version:
            raise DependencyUnavailable('timezone changed during calendar resolution')
        return CashDay(day, state, opened, closed, known, tuple(sources), self.timezone_version, self.version)

    def quarter_dates(self, year: int, quarter: int):
        if type(year) is not int or not 1 <= year <= 9998 or type(quarter) is not int or quarter not in (1, 2, 3, 4):
            raise ContractError('quarter requires an integer civil year and quarter one through four')
        start = date(year, 3 * quarter - 2, 1)
        end = date(year + 1, 1, 1) if quarter == 4 else date(year, 3 * quarter + 1, 1)
        result = []
        while start < end:
            row = self.resolve(start, cut=local_timestamp(start, time(0), self.zone))
            if row.state != 'closed':
                result.append(row)
            start += timedelta(days=1)
        return tuple(result)


@dataclass(frozen=True)
class VenueBoundary:
    day: date
    instrument_root: str
    valid_start: int
    valid_end: int
    required_flat_at: int
    known_at: int
    source_version: str
    scope: str

    def __post_init__(self):
        _date(self.day)
        _label(self.instrument_root)
        _label(self.source_version)
        for at in (self.valid_start, self.valid_end, self.required_flat_at, self.known_at):
            timestamp(at)
        if (self.instrument_root not in ('NQ', 'ES')
                or self.scope not in ('verified_venue_schedule', 'synthetic_research_window')
                or not self.valid_start < self.required_flat_at <= self.valid_end):
            raise ContractError('explicit raw-futures venue boundary and source scope required')


def e0_window(day: CashDay, *, boundary: VenueBoundary, cut: int, safety_buffer_ns: int, require_verified_venue: bool = True):
    if type(day) is not CashDay or type(boundary) is not VenueBoundary or type(require_verified_venue) is not bool:
        raise ContractError('E0 calendar inputs and venue requirement must be explicitly typed')
    timestamp(cut)
    if timestamp(safety_buffer_ns) <= 0:
        raise ContractError('E0 needs a positive integer nanosecond safety buffer')
    if day.state == 'closed':
        raise DependencyUnavailable('no E0 entry window on a closed cash RTH day')
    if day.day != boundary.day or max(day.known_at, boundary.known_at) > cut:
        raise DependencyUnavailable('required session facts unavailable or incompatible')
    if require_verified_venue and boundary.scope != 'verified_venue_schedule':
        raise DependencyUnavailable('cash RTH alone cannot certify a futures venue boundary')
    entry_start = local_timestamp(day.day, time(9, 31), 'America/New_York')
    entry_end = local_timestamp(day.day, time(15, 30), 'America/New_York')
    required = min(day.close_at, boundary.required_flat_at)
    send = min(local_timestamp(day.day, time(15, 55), 'America/New_York'), timestamp(required - safety_buffer_ns))
    if (boundary.valid_start > day.open_at or boundary.valid_end < required or send <= entry_start
            or not day.open_at <= entry_start < day.close_at):
        raise DependencyUnavailable('venue interval does not cover the requested E0 window')
    return {'entry_start': entry_start, 'entry_end': min(entry_end, send), 'flatten_send_at': send,
            'required_flat_at': required, 'calendar_version': day.version, 'boundary_version': digest(boundary),
            'boundary_scope': boundary.scope, 'safety_buffer_ns': safety_buffer_ns}
