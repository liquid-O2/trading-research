"""Exact typed price references from certified sealed ranges and official reports.

The finite M12 engineering surface does not select a tradable universe, infer an
absent settlement, or produce a learned role/reach probability.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.calendar import Calendar, Session
from trading_research.foundations.object_graph import Instrument, PublicationClock, content_hash
from trading_research.foundations.range_primitives import RangePrimitive
from trading_research.foundations.time import timestamp
from trading_research.context.range_adapter import primitive_registry_links, _require_primitive
from trading_research.operations.artifacts import digest

FIELDS = ('open', 'high', 'low', 'close')
REFERENCE_KINDS = frozenset((
    'session_first_eligible_trade', 'first_observed_trade', 'bar_open',
    'session_high', 'session_low', 'session_last_eligible_trade', 'last_observed_trade',
    'official_settlement', 'arithmetic_midpoint', 'vwap', 'body25', 'range25',
    'current_open',
))
_PRIOR_TOKEN = object()


def _name(value):
    if type(value) is not str or not value or len(value.encode()) > 256:
        raise ContractError('bounded nonempty reference identity required')


def _exact(value):
    if type(value) is not Fraction:
        raise ContractError('exact Fraction ticks required')


def _bound(value, maximum=256):
    if type(value) is not int or not 0 < value <= maximum:
        raise ContractError('positive finite configured bound required')


def _clocks(clocks, *, input_known_at, horizon_end, instrument):
    if type(clocks) is not PublicationClock or clocks.actual_completion_at is None:
        raise ContractError('actual derivation completion required')
    timestamp(horizon_end)
    if clocks.input_known_at < input_known_at or input_known_at > clocks.decision_cut:
        raise DependencyUnavailable('reference input unavailable at frozen decision cut')
    if horizon_end <= clocks.known_at:
        raise ContractError('reference horizon expires before publication')
    if not instrument.valid(clocks.known_at) or any(
            end is not None and horizon_end > end
            for end in (instrument.valid_until, instrument.expiry_at)):
        raise DependencyUnavailable('reference horizon outside exact raw lifetime')


def require_primitive(primitive, *, clocks, horizon_end):
    if type(primitive) is not RangePrimitive:
        raise ContractError('certified typed range primitive required')
    # The common port checks its private factory receipt and exact projection.
    if type(clocks) is not PublicationClock:
        raise ContractError('typed publication clocks required')
    _require_primitive(primitive, cut=min(clocks.decision_cut, clocks.input_known_at))
    _clocks(clocks, input_known_at=max(primitive.published_at,
                                     primitive.selection.session.known_at,
                                     primitive.selection.selected_at,
                                     primitive.selection.interval_graph.known_at),
            horizon_end=horizon_end, instrument=primitive.selection.instrument)
    return primitive


@dataclass(frozen=True)
class ReferencePrice:
    id: str
    kind: str
    instrument: Instrument
    value_ticks: Fraction | None
    observed_at: int | None
    known_at: int
    horizon_end: int
    source_versions: tuple[str, ...]
    support: str
    reason: str
    revision: int = 0
    supersedes: str | None = None

    def __post_init__(self):
        for value in (self.id, self.kind, self.reason):
            _name(value)
        if self.kind not in REFERENCE_KINDS or type(self.instrument) is not Instrument:
            raise ContractError('explicit reference type and exact raw instrument required')
        timestamp(self.known_at); timestamp(self.horizon_end)
        if self.horizon_end <= self.known_at:
            raise ContractError('reference needs a future expiry')
        if self.observed_at is not None:
            timestamp(self.observed_at)
            if self.observed_at > self.known_at:
                raise ContractError('future reference observation')
        if (type(self.source_versions) is not tuple or not self.source_versions
                or len(self.source_versions) > 256 or len(set(self.source_versions)) != len(self.source_versions)):
            raise ContractError('bounded immutable source version lineage required')
        for version in self.source_versions:
            _name(version)
        if self.support not in ('observed', 'partial', 'ambiguous', 'empty', 'unavailable'):
            raise ContractError('explicit field support required')
        if self.value_ticks is not None:
            _exact(self.value_ticks)
        if (self.support == 'observed') != (self.value_ticks is not None):
            raise ContractError('unsupported values cannot masquerade as exact prices')
        if type(self.revision) is not int or self.revision < 0:
            raise ContractError('nonnegative exact reference revision required')
        if self.supersedes is not None:
            _name(self.supersedes)

    @property
    def version(self):
        return content_hash(self)

    def available(self, cut):
        timestamp(cut)
        self.__post_init__()
        return (self.support == 'observed' and self.known_at <= cut < self.horizon_end
                and self.instrument.valid(cut))

    def value_at(self, cut):
        return self.value_ticks if self.available(cut) else None


@dataclass(frozen=True)
class ReferenceSet:
    primitive_version: str
    references: tuple[ReferencePrice, ...]
    first_observed: ReferencePrice | None
    last_observed: ReferencePrice | None
    complete_e0: bool
    status: str

    def __post_init__(self):
        _name(self.primitive_version)
        if (type(self.references) is not tuple or len(self.references) != 4
                or any(type(r) is not ReferencePrice for r in self.references)
                or tuple(r.kind for r in self.references)[1:] !=
                   ('session_high', 'session_low', 'session_last_eligible_trade')
                or self.references[0].kind not in ('session_first_eligible_trade', 'bar_open')
                or type(self.complete_e0) is not bool
                or self.complete_e0 != all(r.support == 'observed' for r in self.references)
                or self.status not in ('complete_no_execution', 'complete', 'incomplete_fields')):
            raise ContractError('immutable ordered OHLC references and exact support required')
        for ref, kind in ((self.first_observed, 'first_observed_trade'),
                          (self.last_observed, 'last_observed_trade')):
            if ref is not None and (type(ref) is not ReferencePrice or ref.kind != kind):
                raise ContractError('observed-only endpoint must retain its diagnostic type')

    def field(self, name):
        if name not in FIELDS:
            raise ContractError('unknown OHLC field')
        return self.references[FIELDS.index(name)]


def session_references(primitive, *, clocks, horizon_end, semantic='session'):
    require_primitive(primitive, clocks=clocks, horizon_end=horizon_end)
    if semantic not in ('session', 'bar'):
        raise ContractError('session and bar open semantics must be explicit')
    kinds = (('session_first_eligible_trade' if semantic == 'session' else 'bar_open'),
             'session_high', 'session_low', 'session_last_eligible_trade')
    refs = []
    for field, kind, support in zip(FIELDS, kinds, primitive.field_support):
        if support.field != field:
            raise ContractError('common primitive field order mismatch')
        value = getattr(primitive, field + '_ticks')
        at = (primitive.first_event_at if field == 'open' else
              primitive.last_event_at if field == 'close' else primitive.selection.window.end)
        if support.status != 'observed':
            at = None
        refs.append(ReferencePrice(
            'ref:' + content_hash((primitive.id, semantic, field)), kind,
            primitive.selection.instrument, None if value is None else Fraction(value),
            at, clocks.known_at, horizon_end, (primitive.version_id,),
            support.status, support.reason, primitive.revision, primitive.supersedes))
    observed = []
    for index, at, label in ((0, primitive.first_event_at, 'first'),
                             (3, primitive.last_event_at, 'last')):
        value = primitive.observed_ohlc[index]
        observed.append(None if value is None else ReferencePrice(
            'ref:' + content_hash((primitive.id, label, 'observed-only')),
            'first_observed_trade' if index == 0 else 'last_observed_trade',
            primitive.selection.instrument, Fraction(value), at, clocks.known_at,
            horizon_end, (primitive.version_id,), 'observed',
            'observed event only; no complete session endpoint claim',
            primitive.revision, primitive.supersedes))
    complete = all(r.support == 'observed' for r in refs)
    status = ('complete_no_execution' if primitive.status == 'empty' else
              'complete' if complete else 'incomplete_fields')
    return ReferenceSet(primitive.version_id, tuple(refs), *observed, complete, status)


def range_formula(primitive, *, formula, clocks, horizon_end):
    require_primitive(primitive, clocks=clocks, horizon_end=horizon_end)
    dependencies = {'body25': ('open', 'close'), 'range25': ('high', 'low'),
                    'arithmetic_midpoint': ('high', 'low')}
    if formula not in dependencies:
        raise ContractError('unregistered exact reference formula')
    required = dependencies[formula]
    support = {s.field: s.status for s in primitive.field_support}
    value = None
    if all(support[f] == 'observed' for f in required):
        if formula == 'body25':
            value = Fraction(3 * primitive.close_ticks + primitive.open_ticks, 4)
        elif formula == 'range25':
            value = Fraction(primitive.low_ticks) + Fraction(primitive.high_ticks - primitive.low_ticks, 4)
        else:
            value = Fraction(primitive.high_ticks + primitive.low_ticks, 2)
    return ReferencePrice('ref:' + content_hash((primitive.id, formula)), formula,
                          primitive.selection.instrument, value, primitive.selection.window.end if value is not None else None,
                          clocks.known_at, horizon_end, (primitive.version_id,),
                          'observed' if value is not None else 'unavailable',
                          'exact named formula' if value is not None else 'required source fields unavailable',
                          primitive.revision, primitive.supersedes)


@dataclass(frozen=True)
class PriorSessionSelection:
    current: Session
    prior: Session
    traversed_versions: tuple[str, ...]
    selected_at: int
    _receipt: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        timestamp(self.selected_at)
        if (type(self.current) is not Session or type(self.prior) is not Session
                or type(self.traversed_versions) is not tuple or not self.traversed_versions
                or len(self.traversed_versions) > 256
                or self.traversed_versions[-1] != self.prior.version
                or any(type(v) is not str or not v for v in self.traversed_versions)):
            raise ContractError('exact known calendar predecessor history required')

    @property
    def version(self):
        return digest((self.current.version, self.prior.version, self.traversed_versions, self.selected_at))


def select_prior_session(*, calendar, current_date, instrument_root, cut, max_calendar_days=32):
    if type(calendar) is not Calendar or type(current_date) is not date:
        raise ContractError('actual versioned Calendar and civil date required')
    timestamp(cut); _bound(max_calendar_days)
    current = calendar.resolve(current_date, instrument_root, cut=cut)
    if not current.eligible:
        raise DependencyUnavailable('current session ineligible')
    traversed = []
    for offset in range(1, max_calendar_days + 1):
        # Every intervening date needs an explicit known calendar fact, including
        # nontrading days. A missing row stops selection rather than being skipped.
        prior = calendar.resolve(current_date - timedelta(days=offset), instrument_root, cut=cut)
        traversed.append(prior.version)
        if prior.eligible:
            if prior.close_at > cut or prior.close_at > current.open_at:
                raise DependencyUnavailable('previous eligible session is not completed')
            value = PriorSessionSelection(current, prior, tuple(traversed), cut)
            object.__setattr__(value, '_receipt', (_PRIOR_TOKEN, calendar, instrument_root,
                                                  max_calendar_days, value.version))
            return value
    raise DependencyUnavailable('no prior eligible session inside declared calendar bound')


def require_prior_primitive(primitive, selection, *, current_instrument):
    if type(selection) is not PriorSessionSelection or type(current_instrument) is not Instrument:
        raise ContractError('exact prior-session and instrument binding required')
    receipt = selection._receipt
    if (type(receipt) is not tuple or len(receipt) != 5 or receipt[0] is not _PRIOR_TOKEN
            or receipt[4] != selection.version):
        raise ContractError('prior selection lacks its actual calendar receipt')
    rebuilt = select_prior_session(calendar=receipt[1], current_date=selection.current.trading_date,
        instrument_root=receipt[2], cut=selection.selected_at, max_calendar_days=receipt[3])
    if rebuilt != selection:
        raise ContractError('calendar predecessor differs from the retained selection')
    _require_primitive(primitive)
    if (primitive.selection.session.version != selection.prior.version
            or primitive.selection.window.start != selection.prior.open_at
            or primitive.selection.window.end != selection.prior.close_at):
        raise ContractError('primitive is not the selected exact completed RTH')
    if primitive.selection.instrument != current_instrument:
        raise DependencyUnavailable('explicit_valid_mapping_required')
    return primitive


@dataclass(frozen=True)
class OfficialSettlement:
    report_id: str
    version_id: str
    revision: int
    predecessor: str | None
    instrument: Instrument
    observation_at: int
    published_at: int
    received_at: int
    price_ticks: Fraction
    source_version: str
    kind: str = 'official_settlement'

    def __post_init__(self):
        for value in (self.report_id, self.version_id, self.source_version):
            _name(value)
        if self.kind != 'official_settlement' or type(self.instrument) is not Instrument:
            raise ContractError('official report evidence cannot be replaced by a close or estimate')
        for at in (self.observation_at, self.published_at, self.received_at):
            timestamp(at)
        if self.observation_at > self.published_at or self.published_at > self.received_at:
            raise ContractError('official publication/receipt chronology is invalid')
        _exact(self.price_ticks)
        if type(self.revision) is not int or self.revision < 0:
            raise ContractError('official revision must be a nonnegative integer')
        if (self.revision == 0) != (self.predecessor is None):
            raise ContractError('official correction requires its exact predecessor')


def official_settlement_at(messages, *, cut, clocks, horizon_end, max_versions=256):
    _bound(max_versions); timestamp(cut)
    if type(messages) is not tuple or len(messages) > max_versions:
        raise ContractError('bounded immutable official-message history required')
    prior = None
    seen = set()
    for m in messages:
        if type(m) is not OfficialSettlement or m.version_id in seen:
            raise ContractError('unique typed official messages required')
        if prior is None:
            if m.revision != 0:
                raise ContractError('official history lacks initial report')
        elif (m.report_id != prior.report_id or m.instrument != prior.instrument
              or m.observation_at != prior.observation_at or m.revision != prior.revision + 1
              or m.predecessor != prior.version_id or m.received_at <= prior.received_at):
            raise ContractError('official revision lineage changed')
        seen.add(m.version_id); prior = m
    eligible = tuple(m for m in messages if m.received_at <= cut)
    if not eligible:
        return None
    m = eligible[-1]
    if clocks.decision_cut != cut:
        raise ContractError('official selection and derivation cuts differ')
    _clocks(clocks, input_known_at=m.received_at, horizon_end=horizon_end, instrument=m.instrument)
    return ReferencePrice('ref:' + content_hash((m.instrument.key, m.report_id, m.kind)), m.kind,
                          m.instrument, m.price_ticks, m.observation_at, clocks.known_at,
                          horizon_end, (m.version_id, m.source_version), 'observed',
                          'explicit official report and publication/receipt evidence',
                          m.revision, m.predecessor)


@dataclass(frozen=True)
class ReferenceGap:
    current_version: str
    prior_version: str
    value_ticks: Fraction | None
    convention: str
    status: str


def reference_gap(current, prior, *, cut):
    if type(current) is not ReferencePrice or type(prior) is not ReferencePrice:
        raise ContractError('two explicitly typed references required')
    convention = current.kind + '_minus_' + prior.kind
    if current.instrument != prior.instrument:
        return ReferenceGap(current.version, prior.version, None, convention,
                            'explicit_valid_mapping_required')
    if not current.available(cut) or not prior.available(cut):
        return ReferenceGap(current.version, prior.version, None, convention, 'unavailable')
    return ReferenceGap(current.version, prior.version, current.value_ticks - prior.value_ticks,
                        convention, 'observed')


def ticks_to_points(value, instrument):
    _exact(value)
    if type(instrument) is not Instrument:
        raise ContractError('exact raw instrument required for unit conversion')
    return value * instrument.tick_size_points


def points_to_ticks(value, instrument):
    _exact(value)
    if type(instrument) is not Instrument:
        raise ContractError('exact raw instrument required for unit conversion')
    return value / instrument.tick_size_points
