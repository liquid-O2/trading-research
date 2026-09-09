"""Immutable named clock intervals and independently owned calendar events.

These objects contain calendar facts, never opening prices or inferred market
coverage. A graph is a frozen view at a knowledge cut, not a live calendar feed.
"""

from bisect import bisect_right
from dataclasses import dataclass, field
from datetime import date, time
import json
from types import MappingProxyType

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import Session, local_timestamp
from trading_research.foundations.cash_calendar import zone_version
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import canonical_json, digest


def _name(value):
    if type(value) is not str or not value.strip() or value.strip() != value:
        raise ContractError('clock names and versions must be nonempty exact strings')
    return value


def _dates(values):
    if (type(values) is not tuple or not values or any(type(v) is not date for v in values)
            or tuple(sorted(set(values))) != values):
        raise ContractError('declared calendar dates must be a sorted unique immutable tuple')


@dataclass(frozen=True)
class Span:
    start: int
    end: int

    def __post_init__(self):
        timestamp(self.start)
        timestamp(self.end)
        if self.end <= self.start:
            raise ContractError('clock spans must be positive half-open intervals')


def union_spans(spans):
    """Canonical finite union; adjacency joins but a missing interval stays empty."""
    if type(spans) is not tuple or any(type(v) is not Span for v in spans):
        raise ContractError('span union requires immutable typed intervals')
    result = []
    for span in sorted(spans, key=lambda v: (v.start, v.end)):
        if result and span.start <= result[-1].end:
            result[-1] = Span(result[-1].start, max(result[-1].end, span.end))
        else:
            result.append(span)
    return tuple(result)


def intersect_spans(left, right):
    """Linear intersection of canonical interval sets."""
    left, right = union_spans(left), union_spans(right)
    i = j = 0
    result = []
    while i < len(left) and j < len(right):
        start, end = max(left[i].start, right[j].start), min(left[i].end, right[j].end)
        if start < end:
            result.append(Span(start, end))
        if left[i].end <= right[j].end:
            i += 1
        else:
            j += 1
    return tuple(result)


@dataclass(frozen=True)
class NamedInterval:
    name: str
    owner: str
    spans: tuple[Span, ...]
    known_at: int
    source_version: str
    clock_variant: str
    timezone_version: str
    trading_dates: tuple[date, ...]
    _starts: tuple[int, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        for value in (self.name, self.owner, self.source_version, self.clock_variant, self.timezone_version):
            _name(value)
        timestamp(self.known_at)
        _dates(self.trading_dates)
        if union_spans(self.spans) != self.spans:
            raise ContractError('named intervals must use canonical nonoverlapping spans')
        object.__setattr__(self, '_starts', tuple(s.start for s in self.spans))

    @property
    def version(self):
        return digest({k: v for k, v in vars(self).items() if k != '_starts'})

    @property
    def duration_ns(self):
        return sum(s.end - s.start for s in self.spans)

    def contains(self, at, *, cut):
        timestamp(at)
        if timestamp(cut) < self.known_at:
            raise DependencyUnavailable('interval definition was not available at this cut')
        index = bisect_right(self._starts, at) - 1
        return index >= 0 and at < self.spans[index].end


@dataclass(frozen=True)
class WallRule:
    name: str
    owner: str
    trading_date: date
    start_day: date
    end_day: date
    start_wall: str
    end_wall: str
    zone: str
    clock_variant: str
    timezone_version: str
    known_at: int
    source_version: str
    start_fold: int | None = None
    end_fold: int | None = None

    def __post_init__(self):
        for v in (self.name, self.owner, self.zone, self.clock_variant, self.timezone_version, self.source_version):
            _name(v)
        if any(type(v) is not date for v in (self.trading_date, self.start_day, self.end_day)):
            raise ContractError('wall rules need explicit civil and trading dates')
        timestamp(self.known_at)
        for value in (self.start_wall, self.end_wall):
            if type(value) is not str:
                raise ContractError('wall clocks must be ISO local time strings')
            try:
                parsed = time.fromisoformat(value)
            except ValueError as exc:
                raise ContractError('invalid local wall time') from exc
            if parsed.tzinfo is not None:
                raise ContractError('declare timezone separately from the wall clock')
        for fold in (self.start_fold, self.end_fold):
            if fold is not None and (type(fold) is not int or fold not in (0, 1)):
                raise ContractError('repeated-wall-time fold must be explicit zero or one')

    def compile(self):
        if zone_version(self.zone) != self.timezone_version:
            raise DependencyUnavailable('declared timezone bytes do not match this compiler')
        start = local_timestamp(self.start_day, time.fromisoformat(self.start_wall), self.zone, fold=self.start_fold)
        end = local_timestamp(self.end_day, time.fromisoformat(self.end_wall), self.zone, fold=self.end_fold)
        if zone_version(self.zone) != self.timezone_version:
            raise DependencyUnavailable('timezone bytes changed during wall-rule compilation')
        return NamedInterval(self.name, self.owner, (Span(start, end),), self.known_at,
                             digest(self), self.clock_variant, self.timezone_version, (self.trading_date,))


@dataclass(frozen=True)
class Intersection:
    name: str
    owner: str
    inputs: tuple[str, ...]
    source_version: str
    known_at: int

    def __post_init__(self):
        for v in (self.name, self.owner, self.source_version):
            _name(v)
        timestamp(self.known_at)
        if type(self.inputs) is not tuple or len(self.inputs) < 2:
            raise ContractError('named intersection requires distinct immutable input names')
        for v in self.inputs:
            _name(v)
        if len(set(self.inputs)) != len(self.inputs):
            raise ContractError('intersection input names must be distinct')


# At a shared deadline finish old formation, publish, reset, then start a new one.
EVENT_PRIORITY = MappingProxyType({'calendar_revision': 0, 'reconcile': 1, 'flatten_deadline': 10,
                                  'formation_close': 20, 'publication': 30, 'reset': 40,
                                  'session_close': 50, 'holiday': 55,
                                  'session_open': 60, 'formation_start': 70})


@dataclass(frozen=True)
class CalendarEvent:
    scope: str
    key: str
    owner: str
    kind: str
    effective_at: int
    known_at: int
    source_versions: tuple[str, ...]
    details: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        for v in (self.scope, self.key, self.owner):
            _name(v)
        if type(self.kind) is not str or self.kind not in EVENT_PRIORITY:
            raise ContractError('unknown calendar event action')
        timestamp(self.effective_at)
        timestamp(self.known_at)
        if type(self.source_versions) is not tuple or not self.source_versions:
            raise ContractError('calendar events require immutable source dependencies')
        for v in self.source_versions:
            _name(v)
        if (type(self.details) is not tuple or any(type(p) is not tuple or len(p) != 2
                                                 or any(type(v) is not str for v in p) for p in self.details)
                or len({p[0] for p in self.details}) != len(self.details)):
            raise ContractError('event metadata must be immutable unique string pairs')

    @property
    def logical_id(self):
        return digest((self.scope, self.owner, self.key, self.kind))

    @property
    def event_id(self):
        return digest(self)

    @property
    def order_key(self):
        return (self.effective_at, EVENT_PRIORITY[self.kind], self.owner, self.key, self.event_id)

    def record(self):
        return json.loads(canonical_json(self))

    @classmethod
    def from_record(cls, record):
        if (type(record) is not dict or set(record) != {'scope', 'key', 'owner', 'kind', 'effective_at',
                'known_at', 'source_versions', 'details'} or type(record['source_versions']) is not list
                or type(record['details']) is not list or any(type(p) is not list for p in record['details'])):
            raise ContractError('serialized calendar event has an unsupported shape')
        return cls(**{**record, 'source_versions': tuple(record['source_versions']),
                      'details': tuple(tuple(p) for p in record['details'])})


@dataclass(frozen=True)
class BoundaryRule:
    key: str
    owner: str
    kind: str
    interval: str
    edge: str
    known_at: int
    source_version: str

    def __post_init__(self):
        for v in (self.key, self.owner, self.interval, self.source_version):
            _name(v)
        timestamp(self.known_at)
        if type(self.kind) is not str or self.kind not in EVENT_PRIORITY or self.edge not in ('start', 'end'):
            raise ContractError('calendar boundary needs a declared action and interval edge')


@dataclass(frozen=True, init=False, eq=False)
class IntervalGraph:
    """Frozen interval/event graph; intersection order explicitly supplies the DAG."""

    _scope: str
    _nodes: object
    _events: tuple
    _known_at: int
    _version: str
    _recipe: bytes

    def __init__(self, scope, intervals, *, intersections=(), boundaries=(), points=()):
        _name(scope)
        for values, cls in ((intervals, NamedInterval), (intersections, Intersection),
                            (boundaries, BoundaryRule), (points, CalendarEvent)):
            if type(values) is not tuple or any(type(v) is not cls for v in values):
                raise ContractError('graph inputs must be immutable tuples of declared node types')
        declarations = [(v.owner, v.key) for v in (*boundaries, *points)]
        if len(set(declarations)) != len(declarations):
            raise ContractError('each action key must have exactly one owner declaration, including empty intervals')
        nodes = {}
        for node in intervals:
            if node.name in nodes:
                raise ContractError('duplicate interval name')
            nodes[node.name] = node
        for spec in intersections:
            if spec.name in nodes or any(name not in nodes for name in spec.inputs):
                raise ContractError('intersection name conflict or unresolved/cyclic dependency')
            inputs = [nodes[name] for name in spec.inputs]
            spans = inputs[0].spans
            for node in inputs[1:]:
                spans = intersect_spans(spans, node.spans)
            nodes[spec.name] = NamedInterval(spec.name, spec.owner, spans,
                max(spec.known_at, *(v.known_at for v in inputs)),
                digest((spec, tuple(v.version for v in inputs))),
                'intersection:' + digest(tuple(v.clock_variant for v in inputs)),
                digest(tuple(v.timezone_version for v in inputs)),
                tuple(sorted({d for v in inputs for d in v.trading_dates})))
        events = list(points)
        clocks = [v.known_at for v in nodes.values()] + [v.known_at for v in points]
        for spec in boundaries:
            if spec.interval not in nodes:
                raise ContractError('boundary refers to an undeclared interval')
            node = nodes[spec.interval]
            clocks.append(spec.known_at)
            if not node.spans:
                continue  # Explicit empty interval: no invented boundary event.
            at = node.spans[0].start if spec.edge == 'start' else node.spans[-1].end
            events.append(CalendarEvent(scope, spec.key, spec.owner, spec.kind, at,
                max(node.known_at, spec.known_at), (node.version, spec.source_version),
                (('interval', node.name), ('edge', spec.edge))))
        if not clocks or any(e.scope != scope for e in events):
            raise ContractError('graph needs dated inputs and one explicit scope')
        if len({(e.owner, e.key) for e in events}) != len(events):
            raise ContractError('each action key must have exactly one owner declaration')
        encoded = []
        for node in intervals:
            encoded.append({k: v for k, v in vars(node).items() if k not in ('_starts', 'trading_dates')}
                           | {'trading_dates': [d.isoformat() for d in node.trading_dates]})
        recipe = {'scope': scope, 'intervals': encoded, 'intersections': intersections,
                  'boundaries': boundaries, 'points': [e.record() for e in points]}
        object.__setattr__(self, '_scope', scope)
        object.__setattr__(self, '_nodes', MappingProxyType(nodes))
        object.__setattr__(self, '_events', tuple(sorted(events, key=lambda e: e.order_key)))
        object.__setattr__(self, '_known_at', max(clocks))
        object.__setattr__(self, '_version', digest(recipe))
        object.__setattr__(self, '_recipe', canonical_json(recipe))

    @property
    def scope(self):
        return self._scope

    @property
    def known_at(self):
        return self._known_at

    @property
    def version(self):
        return self._version

    @property
    def intervals(self):
        return self._nodes

    @property
    def events(self):
        return self._events

    def record(self):
        return {'version': self.version, 'definition': json.loads(self._recipe)}

    @classmethod
    def from_record(cls, record):
        if (type(record) is not dict or set(record) != {'version', 'definition'}
                or type(record['definition']) is not dict
                or set(record['definition']) != {'scope', 'intervals', 'intersections', 'boundaries', 'points'}):
            raise ContractError('serialized interval graph has an unsupported shape')
        recipe = record['definition']
        if digest(recipe) != record['version']:
            raise IntegrityError('serialized graph definition does not match its frozen version')
        try:
            if any(type(recipe[k]) is not list for k in ('intervals', 'intersections', 'boundaries', 'points')):
                raise ContractError('serialized graph collections must be JSON arrays')
            nodes = []
            for node in recipe['intervals']:
                if type(node) is not dict or type(node['spans']) is not list or type(node['trading_dates']) is not list:
                    raise ContractError('serialized interval needs explicit span and date arrays')
                dates = tuple(date.fromisoformat(d) for d in node['trading_dates'])
                if [d.isoformat() for d in dates] != node['trading_dates']:
                    raise ContractError('serialized trading dates must use YYYY-MM-DD')
                nodes.append(NamedInterval(**{**node, 'spans': tuple(Span(**s) for s in node['spans']),
                                              'trading_dates': dates}))
            intersections = []
            for spec in recipe['intersections']:
                if type(spec) is not dict or type(spec['inputs']) is not list:
                    raise ContractError('serialized intersection requires explicit input names')
                intersections.append(Intersection(**{**spec, 'inputs': tuple(spec['inputs'])}))
            graph = cls(recipe['scope'], tuple(nodes), intersections=tuple(intersections),
                        boundaries=tuple(BoundaryRule(**v) for v in recipe['boundaries']),
                        points=tuple(CalendarEvent.from_record(v) for v in recipe['points']))
        except (KeyError, ValueError, TypeError) as exc:
            if isinstance(exc, ContractError):
                raise
            raise ContractError('invalid serialized interval graph') from exc
        if graph.record() != record:
            raise IntegrityError('graph reconstruction changed its declared identity')
        return graph

    def query(self, name, at, *, cut):
        _name(name)
        if timestamp(cut) < self.known_at:
            raise DependencyUnavailable('compiled graph was not available at this cut')
        if name not in self._nodes:
            raise DependencyUnavailable('named calendar interval is not registered')
        return self._nodes[name].contains(at, cut=cut)


def session_union(name, owner, sessions, *, source_version):
    """Use supplied dated rows, including explicit ineligible/closed date gaps."""
    if type(sessions) is not tuple or not sessions or any(type(s) is not Session for s in sessions):
        raise ContractError('calendar period requires explicit immutable session rows')
    if len({s.instrument_root for s in sessions}) != 1 or len({s.trading_date for s in sessions}) != len(sessions):
        raise ContractError('calendar period must identify one instrument and each date once')
    _name(source_version)
    return NamedInterval(name, owner, union_spans(tuple(Span(s.open_at, s.close_at) for s in sessions if s.eligible)),
        max(s.known_at for s in sessions), digest((source_version, tuple(s.version for s in sessions))),
        'explicit_dated_session_union', digest(tuple(s.timezone_version for s in sessions)),
        tuple(sorted(s.trading_date for s in sessions)))


def session_graph(session, *, owner='calendar', intervals=(), intersections=(), boundaries=()):
    if type(session) is not Session:
        raise ContractError('session graph requires a typed calendar version')
    _name(owner)
    if type(intervals) is not tuple:
        raise ContractError('session graph needs an immutable interval tuple')
    shared = dict(known_at=session.known_at, source_version=session.version,
                  clock_variant='explicit_dated_session', timezone_version=session.timezone_version,
                  trading_dates=(session.trading_date,))
    market = NamedInterval('session', owner, (Span(session.open_at, session.close_at),), **shared)
    entry = NamedInterval('eligible_entry', owner,
                          (Span(session.open_at, session.flatten_at),) if session.eligible else (), **shared)
    points = tuple(CalendarEvent(session.id, key, owner, key, at, session.known_at, (session.version,),
        (('eligibility_reason', session.eligibility_reason), ('eligible', str(session.eligible))))
        for key, at in (('session_open', session.open_at), ('flatten_deadline', session.flatten_at),
                        ('session_close', session.close_at)))
    return IntervalGraph(session.id, (market, entry) + intervals,
                         intersections=intersections, boundaries=boundaries, points=points)
