"""L03 source-specific prior-session locations and separate freshness observations."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.object_graph import Instrument, content_hash
from trading_research.foundations.time import timestamp
from trading_research.location.edge_extensions import Location, LocationSet, line_geometry, _seal_locations
from trading_research.measurements.reference_prices import (
    require_primitive, require_prior_primitive, _bound, _exact,
)

GENERATOR = 'L03-prior-session-v1'
DEFINITION = 'v1'
FIELDS = ('open', 'high', 'low', 'close')


def prior_locations(primitive, *, clocks, horizon_end, fields=FIELDS,
                    contact_tolerance=Fraction(1), candidate_cap=256,
                    prior_selection=None, current_instrument=None, semantic='prior_RTH'):
    require_primitive(primitive, clocks=clocks, horizon_end=horizon_end)
    _bound(candidate_cap); _exact(contact_tolerance)
    if (type(fields) is not tuple or not fields or len(set(fields)) != len(fields)
            or any(f not in FIELDS for f in fields) or contact_tolerance < 0
            or semantic not in ('prior_RTH', 'full_session', 'current_range')):
        raise ContractError('explicit finite OHLC subset and source interpretation required')
    if len(fields) > candidate_cap:
        raise ContractError('prior candidate cap exceeded before mutation')
    if (prior_selection is None) != (current_instrument is None):
        raise ContractError('prior selection and current raw instrument must be bound together')
    if semantic == 'prior_RTH' and prior_selection is None:
        raise ContractError('prior_RTH requires actual calendar predecessor selection')
    if prior_selection is not None:
        require_prior_primitive(primitive, prior_selection, current_instrument=current_instrument)
        if prior_selection.selected_at > min(clocks.decision_cut, clocks.input_known_at):
            raise DependencyUnavailable('prior calendar choice unavailable at cut')
    supports = {s.field: s.status for s in primitive.field_support}
    output = []
    for field in fields:
        if supports[field] != 'observed':
            continue
        definition = 'def:' + content_hash((GENERATOR, DEFINITION, semantic, field, contact_tolerance))
        output.append(Location('prior_' + field, (),
                               line_geometry(primitive, price=Fraction(getattr(primitive, field + '_ticks')),
                                             tolerance=contact_tolerance, definition=definition),
                               (field,)))
    complete = len(output) == len(fields)
    return _seal_locations(LocationSet(primitive, GENERATOR, DEFINITION, tuple(output), clocks, horizon_end,
                       'observed' if complete else 'unavailable_required_fields',
                       candidate_cap, semantic), prior_locations,
        dict(primitive=primitive, clocks=clocks, horizon_end=horizon_end, fields=fields,
             contact_tolerance=contact_tolerance, candidate_cap=candidate_cap,
             prior_selection=prior_selection, current_instrument=current_instrument, semantic=semantic))


@dataclass(frozen=True)
class ReferenceObservation:
    id: str
    instrument: Instrument
    at: int
    known_at: int
    sequence: int
    price_ticks: Fraction
    session: str
    source_version: str

    def __post_init__(self):
        timestamp(self.at); timestamp(self.known_at); _exact(self.price_ticks)
        if (type(self.id) is not str or not self.id or type(self.instrument) is not Instrument
                or self.at > self.known_at or type(self.sequence) is not int or self.sequence < 0
                or self.session not in ('RTH', 'ETH') or type(self.source_version) is not str
                or not self.source_version):
            raise ContractError('exact available native-event observation and session attribution required')


@dataclass(frozen=True)
class Freshness:
    reference_version: str
    interpretation: str
    contact_event_ids: tuple[str, ...]
    breach_event_ids: tuple[str, ...]
    return_event_ids: tuple[str, ...]
    known_at: int
    role_probability: None = None

    @property
    def touched(self):
        return bool(self.contact_event_ids)

    @property
    def breached(self):
        return bool(self.breach_event_ids)

    @property
    def returned(self):
        return bool(self.return_event_ids)


def reference_freshness(reference, observations, *, cut, side, interpretation='RTH_only', max_events=256):
    _bound(max_events); timestamp(cut)
    if interpretation not in ('RTH_only', 'full_session') or type(side) is not int or side not in (-1, 1):
        raise ContractError('source interpretation and high/low side must be explicit')
    if (type(observations) is not tuple or len(observations) > max_events
            or any(type(o) is not ReferenceObservation for o in observations)):
        raise ContractError('bounded immutable native observation history required')
    if len({o.id for o in observations}) != len(observations):
        raise ContractError('duplicate observation evidence')
    if not reference.available(cut):
        raise DependencyUnavailable('reference unavailable at freshness cut')
    if any(o.instrument != reference.instrument for o in observations):
        raise ContractError('freshness history changes raw instrument')
    visible = sorted((o for o in observations if o.known_at <= cut and o.at >= reference.known_at
                      and (interpretation == 'full_session' or o.session == 'RTH')),
                     key=lambda o: (o.at, o.sequence))
    if len({(o.at, o.sequence) for o in visible}) != len(visible):
        raise ContractError('unresolved duplicate native event ordering')
    contacts, breaches, returns = [], [], []
    crossed = False
    for o in visible:
        delta = side * (o.price_ticks - reference.value_ticks)
        if delta == 0:
            contacts.append(o.id)
        elif delta > 0:
            crossed = True; breaches.append(o.id)
        elif crossed:
            returns.append(o.id)
    return Freshness(reference.version, interpretation, tuple(contacts), tuple(breaches),
                     tuple(returns), cut)
