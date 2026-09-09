"""Finite causal roll/coordinate kernels; no certification of real parent coverage."""

from dataclasses import dataclass, fields, is_dataclass, replace
from decimal import Decimal
from fractions import Fraction
from math import log
from threading import RLock

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import Session
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.time import AvailabilityBasis, Clocks, derived_clocks, timestamp
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.journal import Journal


def _name(value):
    if type(value) is not str or not value:
        raise ContractError('nonempty immutable string identity required')


def _names(values):
    if type(values) is not tuple or any(type(v) is not str or not v for v in values) or len(set(values)) != len(values):
        raise ContractError('immutable unique evidence identities required')


def _live_horizon(horizon_end, *clocks):
    """An explicit input validity end limits a newly published live result."""
    timestamp(horizon_end)
    return min((horizon_end, *(c.valid_until for c in clocks if c.valid_until is not None)))


def _currency(value):
    if type(value) is not str or len(value) != 3 or not value.isascii() or not value.isupper() or not value.isalpha():
        raise ContractError('explicit three-letter cash currency required')


def _fraction(value, *, positive=False, nonnegative=False):
    if type(value) is not Fraction or positive and value <= 0 or nonnegative and value < 0:
        raise ContractError('exact Fraction with the declared sign required')


def _integer(value, *, minimum=0):
    if type(value) is not int or value < minimum:
        raise ContractError('exact bounded nonnegative integer required')


@dataclass(frozen=True)
class ContractUniverse:
    id: str
    root: str
    known_at: int
    contract_ids: tuple[str, ...]
    coverage_scope: str
    source_version: str
    provider: str | None = None
    venue: str | None = None
    lifetimes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        for v in (self.id, self.root, self.source_version): _name(v)
        timestamp(self.known_at); _names(self.contract_ids)
        if not self.contract_ids or self.coverage_scope not in ('complete_parent_outrights', 'acquired_outright_cohort', 'synthetic_complete_parent_fixture'):
            raise ContractError('declared parent/acquired/synthetic universe scope required')
        if (self.provider is None) != (self.venue is None):
            raise ContractError('declare provider and venue together')
        if self.provider is not None: _name(self.provider); _name(self.venue)
        if type(self.lifetimes) is not tuple or any(type(p) is not tuple or len(p) != 2 for p in self.lifetimes):
            raise ContractError('immutable instrument lifetime bindings required')
        for key, value in self.lifetimes: _name(key); _name(value)
        if self.lifetimes and (len(dict(self.lifetimes)) != len(self.lifetimes) or set(dict(self.lifetimes)) != set(self.contract_ids)):
            raise ContractError('lifetime bindings must cover the declared universe exactly')

    @property
    def version(self): return digest(self)


@dataclass(frozen=True)
class SessionVolume:
    instrument_id: str
    session_id: str
    session_start: int
    session_end: int
    known_at: int
    contracts: int
    complete: bool
    source_version: str
    instrument_lifetime: str | None = None

    def __post_init__(self):
        for v in (self.instrument_id, self.session_id, self.source_version): _name(v)
        for v in (self.session_start, self.session_end, self.known_at): timestamp(v)
        _integer(self.contracts)
        if type(self.complete) is not bool or self.session_end <= self.session_start or self.known_at < self.session_end:
            raise ContractError('volume needs an explicit completed session and availability')
        if self.instrument_lifetime is not None: _name(self.instrument_lifetime)

    @property
    def version(self): return digest(self)


@dataclass(frozen=True)
class SessionSequence:
    """Version-resolved finite venue calendar evidence, not an inferred calendar."""
    id: str
    root: str
    sessions: tuple[Session, ...]
    known_at: int
    source_version: str
    complete: bool

    def __post_init__(self):
        for v in (self.id, self.root, self.source_version): _name(v)
        timestamp(self.known_at)
        if (type(self.sessions) is not tuple or len(self.sessions) < 2 or any(type(s) is not Session for s in self.sessions)
                or type(self.complete) is not bool or len({s.id for s in self.sessions}) != len(self.sessions)):
            raise ContractError('finite immutable version-resolved session sequence required')
        if any(s.instrument_root != self.root or s.known_at > self.known_at for s in self.sessions):
            raise ContractError('calendar scope/availability differs from its supplied rows')
        if any(a.close_at > b.open_at for a, b in zip(self.sessions, self.sessions[1:])):
            raise ContractError('calendar rows must be ordered and nonoverlapping')

    def preceding(self, cut):
        timestamp(cut)
        if not self.complete or self.known_at > cut:
            raise DependencyUnavailable('complete predecessor calendar was unavailable')
        for i, session in enumerate(self.sessions):
            if session.open_at <= cut < session.close_at:
                if i == 0 or not session.eligible or not self.sessions[i-1].eligible:
                    raise DependencyUnavailable('required current/preceding session unavailable')
                return self.sessions[i-1], session
        raise DependencyUnavailable('cut is outside the finite declared venue calendar')

    @property
    def version(self): return digest(self)


def _definitions(universe, definitions, cut):
    timestamp(cut)
    if type(universe) is not ContractUniverse or type(definitions) is not tuple or any(type(d) is not InstrumentDefinition for d in definitions):
        raise ContractError('typed immutable universe/definitions required')
    if universe.known_at > cut: raise DependencyUnavailable('future contract universe')
    by = {d.key.instrument_id: d for d in definitions}
    if len(by) != len(definitions):
        raise ContractError('ambiguous numeric definition ID; resolve namespace/lifetime/revisions first')
    namespaces = {(d.key.provider, d.key.venue) for d in definitions if d.key.instrument_id in universe.contract_ids}
    if len(namespaces) != 1 or universe.provider is not None and namespaces != {(universe.provider, universe.venue)}:
        raise ContractError('roll universe cannot silently cross provider/venue namespaces')
    considered, eligible, excluded = [], {}, {}
    bindings = dict(universe.lifetimes)
    for key in universe.contract_ids:
        d = by.get(key)
        if d is None or d.clocks.known_at > cut:
            raise DependencyUnavailable('an admitted contract lacks an available definition')
        if bindings and bindings[key] != instrument_identity(d):
            raise ContractError('definition differs from the declared instrument lifetime')
        ok, reason = d.eligibility('execution')
        ok = ok and d.clocks.available(cut, valid_at=cut) and d.classification == 'future' and d.key.underlying == universe.root and d.key.expiry_at is not None and d.key.expiry_at > cut
        if not ok: excluded[key] = reason if reason != 'known purpose-specific terms' else 'not an unexpired outright of this root'
        else: eligible[key] = d
        considered.append((key, d.key.definition_version, instrument_identity(d), d.clocks.known_at, ok, excluded.get(key, 'eligible')))
    if not eligible: raise DependencyUnavailable('no eligible unexpired outright')
    return eligible, tuple(considered), excluded


def select_prior_volume(*, universe, definitions, volumes, previous_session_id, cut, session_sequence=None):
    """Unpublished scalar reference result. Its input clock is not publication."""
    _name(previous_session_id)
    if type(volumes) is not tuple or any(type(v) is not SessionVolume for v in volumes):
        raise ContractError('typed immutable volume records required')
    eligible, considered, excluded = _definitions(universe, definitions, cut)
    previous = current = None
    if session_sequence is not None:
        if type(session_sequence) is not SessionSequence or session_sequence.root != universe.root:
            raise ContractError('typed matching predecessor calendar required')
        previous, current = session_sequence.preceding(cut)
        if previous.id != previous_session_id: raise ContractError('not the immediately preceding venue session')
    selected_rows = []
    scanned = 0
    for key, definition in eligible.items():
        rows = []
        for v in volumes:
            scanned += 1
            if v.instrument_id == key and v.session_id == previous_session_id and v.known_at <= cut:
                rows.append(v)
        if not rows: raise DependencyUnavailable('missing previous-session volume for an eligible competitor')
        latest = max(v.known_at for v in rows)
        rows = list({v.version: v for v in rows if v.known_at == latest}.values())
        if len(rows) != 1 or not rows[0].complete or rows[0].session_end > cut:
            raise DependencyUnavailable('ambiguous/incomplete previous-session volume')
        row = rows[0]
        if previous and (row.session_start, row.session_end) != (previous.open_at, previous.close_at):
            raise ContractError('volume interval differs from the actual preceding session')
        if row.instrument_lifetime is not None and row.instrument_lifetime != instrument_identity(definition):
            raise ContractError('volume belongs to another instrument lifetime')
        if universe.lifetimes and row.instrument_lifetime is None:
            raise DependencyUnavailable('qualified universe needs qualified volume lineage')
        selected_rows.append((definition, row))
    if len({(v.session_start, v.session_end) for _, v in selected_rows}) != 1:
        raise ContractError('competitors must cover the same completed session interval')
    selected = min(selected_rows, key=lambda p: (-p[1].contracts, p[0].key.expiry_at, instrument_identity(p[0])))
    # Keep legacy canonical numeric-ID tie semantics after expiry ties.
    tied = [p for p in selected_rows if (p[1].contracts, p[0].key.expiry_at) == (selected[1].contracts, selected[0].key.expiry_at)]
    selected = min(tied, key=lambda p: p[0].key.instrument_id)
    body = {'instrument_id': selected[0].key.instrument_id, 'instrument_lifetime': instrument_identity(selected[0]),
            'definition_version': selected[0].key.definition_version, 'decision_cut': cut, 'published': False,
            'input_known_at': max(universe.known_at, *(r[3] for r in considered), *(v.known_at for _, v in selected_rows),
                                  session_sequence.known_at if session_sequence else universe.known_at),
            'universe_version': universe.version, 'universe_scope': universe.coverage_scope,
            'preceding_session': previous_session_id, 'calendar_version': session_sequence.version if session_sequence else None,
            'definitions': considered, 'volume_evidence': tuple(v for _, v in selected_rows),
            'volumes': {d.key.instrument_id: v.contracts for d, v in selected_rows}, 'excluded': excluded,
            'volume_rows_examined': scanned, 'selection_basis': 'preceding complete session volume, then earlier expiry, then canonical ID; conditional on declared universe'}
    return {**body, 'version': digest(body)}


@dataclass(frozen=True)
class RawCoordinate:
    provider: str
    venue: str
    instrument_id: str
    lifetime: str
    root: str
    tick_size: Fraction
    multiplier: Fraction
    currency: str
    currency_evidence_id: str
    valid_from: int
    valid_until: int

    def __post_init__(self):
        for v in (self.provider, self.venue, self.instrument_id, self.lifetime, self.root, self.currency_evidence_id): _name(v)
        _currency(self.currency)
        _fraction(self.tick_size, positive=True); _fraction(self.multiplier, positive=True)
        timestamp(self.valid_from); timestamp(self.valid_until)
        if self.valid_until <= self.valid_from: raise ContractError('invalid raw coordinate lifetime')

    @classmethod
    def from_definition(cls, definition, *, currency, currency_evidence_id):
        """Currency is supplied evidence; InstrumentDefinition does not contain it."""
        if type(definition) is not InstrumentDefinition or not definition.eligibility('execution')[0]:
            raise DependencyUnavailable('execution terms unavailable for raw coordinate')
        _currency(currency); _name(currency_evidence_id)
        d = definition
        valid_until = min(d.clocks.valid_until, d.key.expiry_at) if d.key.expiry_at is not None else d.clocks.valid_until
        return cls(d.key.provider, d.key.venue, d.key.instrument_id, instrument_identity(d), d.key.underlying,
                   Fraction(d.tick_size), Fraction(d.multiplier), currency, currency_evidence_id,
                   d.clocks.valid_from, valid_until)

    @property
    def version(self): return digest(self)

    def available(self, at): return self.valid_from <= timestamp(at) < self.valid_until


@dataclass(frozen=True)
class PublicationTiming:
    input_known_at: int
    decision_cut: int
    actual_completion_at: int
    horizon_end: int

    def __post_init__(self):
        for v in (self.input_known_at, self.decision_cut, self.actual_completion_at, self.horizon_end): timestamp(v)
        if self.input_known_at > self.decision_cut or self.actual_completion_at < self.decision_cut:
            raise ContractError('freeze inputs at the cut and retain actual completion afterward')
        if self.horizon_end <= self.actual_completion_at:
            raise DependencyUnavailable('original horizon elapsed before publication')

    @property
    def known_at(self): return max(self.input_known_at, self.actual_completion_at)

    def available(self, at): return self.known_at <= timestamp(at) < self.horizon_end


@dataclass(frozen=True)
class RollPolicy:
    id: str
    name: str

    def __post_init__(self):
        _name(self.id)
        if self.name not in ('preceding_volume', 'fixed_calendar', 'provider_map'):
            raise ContractError('unknown separately named roll policy')

    @property
    def version(self): return digest(self)


@dataclass(frozen=True)
class ContractMap:
    id: str
    policy: RollPolicy
    universe_version: str
    coordinate: RawCoordinate
    effective_at: int
    valid_until: int
    clocks: Clocks

    def __post_init__(self):
        _name(self.id); _name(self.universe_version)
        timestamp(self.effective_at); timestamp(self.valid_until)
        if type(self.policy) is not RollPolicy or self.policy.name == 'preceding_volume' or type(self.coordinate) is not RawCoordinate or type(self.clocks) is not Clocks:
            raise ContractError('typed source/fixed contract mapping required')
        if self.valid_until <= self.effective_at: raise ContractError('invalid map interval')

    @property
    def version(self): return digest(self)


@dataclass(frozen=True)
class RollSelection:
    id: str
    policy: RollPolicy
    universe: ContractUniverse
    coordinate: RawCoordinate
    timing: PublicationTiming
    evidence_versions: tuple[str, ...]
    definition_evidence: tuple[tuple, ...]
    volume_evidence: tuple[SessionVolume, ...]
    calendar: SessionSequence | None
    source_map: ContractMap | None
    operations: int
    definitions: tuple[InstrumentDefinition, ...]
    volume_inputs: tuple[SessionVolume, ...]
    map_inputs: tuple[ContractMap, ...]
    requested_horizon_end: int
    currency: str
    currency_evidence_id: str

    def __post_init__(self):
        _name(self.id); _names(self.evidence_versions); _integer(self.operations)
        _currency(self.currency); _name(self.currency_evidence_id); timestamp(self.requested_horizon_end)
        if (type(self.policy) is not RollPolicy or type(self.universe) is not ContractUniverse
                or type(self.coordinate) is not RawCoordinate or type(self.timing) is not PublicationTiming
                or type(self.definition_evidence) is not tuple
                or type(self.volume_evidence) is not tuple):
            raise ContractError('immutable complete selection evidence required')
        expected = _selection_components(policy=self.policy, universe=self.universe, definitions=self.definitions,
            cut=self.timing.decision_cut, completed_at=self.timing.actual_completion_at,
            horizon_end=self.requested_horizon_end, currency=self.currency, currency_evidence_id=self.currency_evidence_id,
            volumes=self.volume_inputs, session_sequence=self.calendar, maps=self.map_inputs)
        if any(getattr(self, key) != value for key, value in expected.items()):
            raise IntegrityError('selection differs from its retained frozen selector inputs')

    @property
    def version(self): return digest(self)
    @property
    def known_at(self): return self.timing.known_at
    def available(self, at): return self.timing.available(at) and self.coordinate.available(at)


def _selection_components(*, policy, universe, definitions, cut, completed_at, horizon_end,
                          currency, currency_evidence_id, volumes, session_sequence, maps):
    """Reconstruct a selection without constructing a derived selection recursively."""
    if type(policy) is not RollPolicy or type(universe) is not ContractUniverse:
        raise ContractError('typed named roll policy and universe required')
    _currency(currency); _name(currency_evidence_id)
    if universe.provider is None or not universe.lifetimes:
        raise DependencyUnavailable('published selection needs explicit namespaced lifetime bindings')
    if (type(volumes) is not tuple or any(type(v) is not SessionVolume for v in volumes)
            or type(maps) is not tuple or any(type(m) is not ContractMap for m in maps)):
        raise ContractError('immutable retained selector inputs required')
    eligible, considered, _ = _definitions(universe, definitions, cut)
    if any(d.clocks.known_at > cut for d in definitions) or any(v.known_at > cut for v in volumes) or any(m.clocks.known_at > cut for m in maps):
        raise ContractError('retained decision inputs must be frozen at the cut')
    source_map = None; rows = (); calendar = None; operations = len(considered)
    evidence = [universe.version, policy.version, currency_evidence_id, *(digest(d) for d in definitions)]
    # Historical excluded definitions remain evidence. Live eligible definitions
    # and their expiry/validity constrain how long this decision may be used.
    horizon_end = min(horizon_end, *(min(d.clocks.valid_until, d.key.expiry_at) for d in eligible.values()))
    if policy.name == 'preceding_volume':
        if maps or type(session_sequence) is not SessionSequence:
            raise ContractError('volume policy requires only its typed predecessor calendar and volume inputs')
        previous, current = session_sequence.preceding(cut)
        result = select_prior_volume(universe=universe, definitions=definitions, volumes=volumes,
                                     previous_session_id=previous.id, cut=cut, session_sequence=session_sequence)
        coordinate = RawCoordinate.from_definition(eligible[result['instrument_id']],
            currency=currency, currency_evidence_id=currency_evidence_id)
        rows, calendar = result['volume_evidence'], session_sequence
        input_known = result['input_known_at']; horizon_end = min(horizon_end, current.close_at)
        operations += result['volume_rows_examined']
        evidence.extend((calendar.version, *(v.version for v in rows)))
    else:
        if volumes or session_sequence is not None:
            raise ContractError('fixed/provider policy has mapping inputs, not a volume/calendar fallback')
        candidates = [m for m in maps if m.policy == policy and m.universe_version == universe.version
                      and m.clocks.available(cut) and m.effective_at <= cut < m.valid_until]
        if not candidates: raise DependencyUnavailable('known-time policy mapping unavailable')
        latest = max(m.clocks.known_at for m in candidates)
        candidates = list({m.version: m for m in candidates if m.clocks.known_at == latest}.values())
        if len(candidates) != 1: raise ContractError('ambiguous simultaneous policy map')
        source_map = candidates[0]; coordinate = source_map.coordinate
        if coordinate.instrument_id not in eligible or coordinate != RawCoordinate.from_definition(eligible[coordinate.instrument_id],
                currency=currency, currency_evidence_id=currency_evidence_id):
            raise ContractError('policy map differs from eligible raw contract definition/currency evidence')
        input_known = max(universe.known_at, *(r[3] for r in considered), source_map.clocks.known_at)
        horizon_end = _live_horizon(min(horizon_end, source_map.valid_until), source_map.clocks)
        evidence.append(source_map.version); operations += len(maps)
    timing = PublicationTiming(input_known, cut, completed_at, min(horizon_end, coordinate.valid_until))
    return {'coordinate': coordinate, 'timing': timing, 'evidence_versions': tuple(dict.fromkeys(evidence)),
            'definition_evidence': considered, 'volume_evidence': rows, 'calendar': calendar,
            'source_map': source_map, 'operations': operations}


def select_roll(*, id, policy, universe, definitions, cut, completed_at, horizon_end,
                currency, currency_evidence_id, volumes=(), session_sequence=None, maps=()):
    # Do not bind a decision to a future suffix it could not yet have observed.
    if (type(definitions) is not tuple or any(type(d) is not InstrumentDefinition for d in definitions)
            or type(volumes) is not tuple or any(type(v) is not SessionVolume for v in volumes)
            or type(maps) is not tuple or any(type(m) is not ContractMap for m in maps)):
        raise ContractError('typed immutable selector inputs required')
    timestamp(cut)
    definitions = tuple(d for d in definitions if d.clocks.known_at <= cut)
    volumes = tuple(v for v in volumes if v.known_at <= cut)
    maps = tuple(m for m in maps if m.clocks.known_at <= cut)
    # A caller may supply common comparison inputs; each named policy retains
    # only its own inputs instead of pretending another selector is a fallback.
    if type(policy) is not RollPolicy: raise ContractError('typed named roll policy required')
    if policy.name == 'preceding_volume': maps = ()
    else: volumes, session_sequence = (), None
    result = _selection_components(policy=policy, universe=universe, definitions=definitions, cut=cut,
        completed_at=completed_at, horizon_end=horizon_end, currency=currency, currency_evidence_id=currency_evidence_id,
        volumes=volumes, session_sequence=session_sequence, maps=maps)
    return RollSelection(id=id, policy=policy, universe=universe, **result, definitions=definitions,
                         volume_inputs=volumes, map_inputs=maps, requested_horizon_end=horizon_end,
                         currency=currency, currency_evidence_id=currency_evidence_id)


@dataclass(frozen=True)
class PriceObservation:
    id: str
    coordinate: RawCoordinate
    observed_at: int
    clocks: Clocks
    price: Fraction
    eligible: bool
    clock_domain: str

    def __post_init__(self):
        _name(self.id); _name(self.clock_domain); timestamp(self.observed_at); _fraction(self.price)
        if type(self.coordinate) is not RawCoordinate or type(self.clocks) is not Clocks or type(self.eligible) is not bool:
            raise ContractError('typed raw observation with explicit eligibility required')
        if self.observed_at > self.clocks.known_at or not self.coordinate.available(self.observed_at):
            raise ContractError('observation clock/lifetime mismatch')

    @property
    def version(self): return digest(self)

    def available(self, at):
        """Live use obeys both the evidence validity and the raw coordinate."""
        return self.eligible and self.clocks.available(at) and self.coordinate.available(at)

    def historical_available(self, at):
        """Explicit audit lookup at original observation validity, not a live quote."""
        return (self.eligible and self.clocks.available(at, valid_at=self.observed_at)
                and self.coordinate.available(self.observed_at))


@dataclass(frozen=True)
class BridgePolicy:
    id: str
    maximum_quote_skew_ns: int
    maximum_quote_age_ns: int

    def __post_init__(self):
        _name(self.id); _integer(self.maximum_quote_skew_ns); _integer(self.maximum_quote_age_ns)

    @property
    def version(self): return digest(self)


@dataclass(frozen=True)
class RollBridge:
    id: str
    old: PriceObservation
    new: PriceObservation
    policy: BridgePolicy
    uncertainty_points: Fraction
    timing: PublicationTiming

    def __post_init__(self):
        _name(self.id); _fraction(self.uncertainty_points, nonnegative=True)
        if type(self.old) is not PriceObservation or type(self.new) is not PriceObservation or type(self.policy) is not BridgePolicy or type(self.timing) is not PublicationTiming:
            raise ContractError('paired typed observations and timing required')
        if self.old.coordinate.lifetime == self.new.coordinate.lifetime or (self.old.coordinate.root, self.old.coordinate.currency, self.old.coordinate.multiplier) != (self.new.coordinate.root, self.new.coordinate.currency, self.new.coordinate.multiplier):
            raise ContractError('roll requires distinct commensurate raw contract lifetimes')
        if self.old.clock_domain != self.new.clock_domain:
            raise DependencyUnavailable('unreconciled observation clock domains')
        if self.timing.horizon_end > _live_horizon(min(self.old.coordinate.valid_until, self.new.coordinate.valid_until), self.old.clocks, self.new.clocks):
            raise ContractError('bridge horizon exceeds its original live input validity')
        if self.timing.input_known_at != max(self.old.clocks.known_at, self.new.clocks.known_at):
            raise ContractError('bridge input clock differs from its observations')
        if not self.old.eligible or not self.new.eligible or not self._usable(self.timing.decision_cut) or not self._usable(self.timing.actual_completion_at):
            raise DependencyUnavailable('missing, stale, future or asynchronous eligible bridge')

    @property
    def observation_interval(self): return (min(self.old.observed_at, self.new.observed_at), max(self.old.observed_at, self.new.observed_at))
    @property
    def spread(self): return self.new.price - self.old.price
    @property
    def version(self): return digest(self)
    @property
    def known_at(self): return self.timing.known_at

    def _usable(self, at):
        skew = abs(self.old.observed_at-self.new.observed_at) + self.old.clocks.clock_uncertainty_ns + self.new.clocks.clock_uncertainty_ns
        return (skew <= self.policy.maximum_quote_skew_ns and at-self.observation_interval[0] <= self.policy.maximum_quote_age_ns
                and self.old.available(at) and self.new.available(at))

    def available(self, at): return self.timing.available(at) and self._usable(at)

    def translate(self, price, *, coordinate, at):
        _fraction(price)
        if coordinate != self.old.coordinate: raise ContractError('wrong source namespace/lifetime/grid')
        if not self.available(at): raise DependencyUnavailable('bridge is not usable at this cut')
        return price + self.spread


def build_bridge(*, id, old, new, policy, uncertainty_points, cut, completed_at, horizon_end):
    if type(old) is not PriceObservation or type(new) is not PriceObservation:
        raise DependencyUnavailable('both eligible raw quote observations are required')
    horizon_end = _live_horizon(min(horizon_end, old.coordinate.valid_until, new.coordinate.valid_until), old.clocks, new.clocks)
    timing = PublicationTiming(max(old.clocks.known_at, new.clocks.known_at), cut, completed_at, horizon_end)
    return RollBridge(id, old, new, policy, uncertainty_points, timing)


@dataclass(frozen=True)
class RollMapping:
    """Legacy finite scalar wrapper; unspecified age allows only its known cut."""
    id: str
    source_instrument: str
    destination_instrument: str
    old_quote_at: int
    new_quote_at: int
    known_at: int
    old_price: Fraction
    new_price: Fraction
    maximum_quote_skew_ns: int
    uncertainty_ticks: Fraction
    evidence_version: str
    maximum_quote_age_ns: int | None = None

    def __post_init__(self):
        for v in (self.id, self.source_instrument, self.destination_instrument, self.evidence_version): _name(v)
        for v in (self.old_quote_at, self.new_quote_at, self.known_at): timestamp(v)
        _fraction(self.old_price); _fraction(self.new_price); _fraction(self.uncertainty_ticks, nonnegative=True)
        _integer(self.maximum_quote_skew_ns)
        if self.maximum_quote_age_ns is not None: _integer(self.maximum_quote_age_ns)
        if self.source_instrument == self.destination_instrument or self.known_at < max(self.old_quote_at, self.new_quote_at):
            raise ContractError('observed distinct raw contracts and availability required')
        if abs(self.new_quote_at-self.old_quote_at) > self.maximum_quote_skew_ns:
            raise DependencyUnavailable('simultaneous-spread mapping too asynchronous')

    def translate(self, price, *, cut, source_instrument):
        _fraction(price); timestamp(cut); _name(source_instrument)
        if cut < self.known_at or source_instrument != self.source_instrument:
            raise DependencyUnavailable('future/wrong-coordinate roll mapping')
        if self.maximum_quote_age_ns is None and cut != self.known_at or self.maximum_quote_age_ns is not None and cut-min(self.old_quote_at, self.new_quote_at) > self.maximum_quote_age_ns:
            raise DependencyUnavailable('stale bridge or no declared later-use age policy')
        return {'raw_destination_price': price+self.new_price-self.old_price, 'mapping_version': digest(self),
                'mapping_uncertainty': self.uncertainty_ticks, 'origin_instrument': self.source_instrument,
                'instrument': self.destination_instrument, 'published': False, 'input_known_at': self.known_at}


def roll_adjusted_change(*, previous_old_price, current_new_price, mapping, cut):
    _fraction(current_new_price)
    translated = mapping.translate(previous_old_price, cut=cut, source_instrument=mapping.source_instrument)
    return current_new_price-translated['raw_destination_price']


def coordinate_change(previous, current, *, kind='points'):
    _fraction(previous); _fraction(current)
    if kind == 'points': return current-previous
    if kind == 'simple':
        if previous == 0: raise ContractError('simple return denominator is zero')
        return (current-previous)/previous
    if kind == 'log':
        if previous <= 0 or current <= 0: raise ContractError('log return requires positive operands')
        return log(current/previous)
    raise ContractError('declare point/simple/log change domain')


def tick_distance(value, source, destination):
    _fraction(value)
    if type(source) is not RawCoordinate or type(destination) is not RawCoordinate or (source.root, source.currency, source.multiplier) != (destination.root, destination.currency, destination.multiplier):
        raise ContractError('commensurate typed point/tick coordinates required')
    return value*source.tick_size/destination.tick_size


@dataclass(frozen=True)
class CoordinateState:
    id: str
    coordinate: RawCoordinate
    kind: str
    values: tuple[Fraction, ...]
    masses: tuple[int, ...]
    clocks: Clocks
    lineage: tuple[str, ...]
    horizon_end: int
    chain: tuple[str, ...] = ()
    active: bool = True
    uncertainty_points: Fraction = Fraction(0)
    exposure_lineage: tuple[str, ...] = ()
    cost_lineage: tuple[str, ...] = ()

    def __post_init__(self):
        _name(self.id); _names(self.lineage); _names(self.chain); _names(self.exposure_lineage); _names(self.cost_lineage)
        timestamp(self.horizon_end); _fraction(self.uncertainty_points, nonnegative=True)
        if type(self.coordinate) is not RawCoordinate or type(self.clocks) is not Clocks or type(self.active) is not bool:
            raise ContractError('typed immutable coordinate state required')
        if self.kind not in ('level', 'band', 'profile', 'point_scale') or type(self.values) is not tuple or type(self.masses) is not tuple or not self.lineage:
            raise ContractError('declared finite state geometry and evidence required')
        for v in self.values: _fraction(v)
        for v in self.masses: _integer(v)
        if self.horizon_end <= self.clocks.known_at: raise DependencyUnavailable('state expired at publication')
        if self.active:
            if not self.values or self.kind in ('level', 'point_scale') and len(self.values) != 1 or self.kind == 'band' and (len(self.values) != 2 or self.values[0] > self.values[1]):
                raise ContractError('state shape differs from its declared kind')
            if self.kind == 'point_scale' and self.values[0] < 0: raise ContractError('point scale cannot be negative')
            if self.kind == 'profile' and (len(self.values) != len(self.masses) or tuple(sorted(set(self.values))) != self.values):
                raise ContractError('profile needs ordered unique raw prices and conserved masses')
            if self.kind != 'profile' and self.masses: raise ContractError('only profile state carries node mass')
        elif self.values or self.masses:
            raise ContractError('reset state cannot retain apparently usable numeric values')

    @property
    def version(self): return digest(self)
    @property
    def known_at(self): return self.clocks.known_at
    @property
    def on_grid(self): return all((v/self.coordinate.tick_size).denominator == 1 for v in self.values)
    def available(self, at): return self.active and self.clocks.available(at) and self.coordinate.available(at) and at < self.horizon_end


@dataclass(frozen=True)
class RollLimits:
    max_records: int = 4096
    max_bytes: int = 8*1024**2
    max_profile_nodes: int = 1024
    max_chain: int = 32

    def __post_init__(self):
        for v in (self.max_records, self.max_bytes, self.max_profile_nodes, self.max_chain): _integer(v, minimum=1)


@dataclass(frozen=True)
class TransitionRecord:
    id: str
    mode: str
    source: CoordinateState
    destination: CoordinateState
    bridge: RollBridge | None
    timing: PublicationTiming
    reason: str
    operations: int

    def __post_init__(self):
        _name(self.id); _name(self.reason); _integer(self.operations)
        if self.mode not in ('translate', 'carry', 'reset') or type(self.source) is not CoordinateState or type(self.destination) is not CoordinateState or type(self.timing) is not PublicationTiming or self.bridge is not None and type(self.bridge) is not RollBridge:
            raise ContractError('typed explicit coordinate transition required')
        if self.destination.clocks.known_at != self.timing.known_at or self.destination.horizon_end != self.timing.horizon_end:
            raise ContractError('transition clocks/horizon differ from destination')

    @property
    def version(self): return digest(self)
    @property
    def known_at(self): return self.timing.known_at
    def available(self, at): return self.timing.available(at)


def transition_state(*, id, source, destination, mode, cut, completed_at, horizon_end, reason,
                     bridge=None, limits=RollLimits()):
    if type(source) is not CoordinateState or type(destination) is not RawCoordinate or type(limits) is not RollLimits:
        raise ContractError('typed source/destination state and bounds required')
    if not source.available(cut): raise DependencyUnavailable('source state unavailable at frozen cut')
    if not destination.available(cut) or source.coordinate.lifetime == destination.lifetime:
        raise ContractError('transition requires a distinct valid destination lifetime')
    if len(source.values) > limits.max_profile_nodes or len(source.chain)+1 > limits.max_chain:
        raise ContractError('profile/transition chain materialization bound exceeded')
    _name(id); _name(reason)
    if id in source.chain: raise ContractError('transition already applied to this state')
    clocks = [source.clocks]; evidence = [source.version]
    values = (); masses = (); uncertainty = source.uncertainty_points; operations = 0
    if mode in ('translate', 'carry'):
        if type(bridge) is not RollBridge or bridge.old.coordinate != source.coordinate or bridge.new.coordinate != destination:
            raise DependencyUnavailable('matching typed bridge required; explicit reset is available')
        if not bridge.available(cut) or not bridge.available(completed_at):
            raise DependencyUnavailable('bridge unavailable/stale before transition publication')
        bridge_clock = Clocks(None, bridge.known_at, bridge.version, AvailabilityBasis.COMPUTED, computed_at=bridge.timing.actual_completion_at)
        clocks.append(bridge_clock); evidence.append(bridge.version)
        if mode == 'carry':
            if source.kind != 'point_scale': raise ContractError('only declared additive-invariant point scale may carry')
            values = source.values
        else:
            if source.kind == 'point_scale': raise ContractError('point scale is not an absolute price level')
            values = tuple(v+bridge.spread for v in source.values); operations = len(values)
            masses = source.masses; uncertainty += bridge.uncertainty_points
        horizon_end = min(horizon_end, bridge.timing.horizon_end)
    elif mode != 'reset' or bridge is not None:
        raise ContractError('reset has no fabricated bridge; select translate/carry/reset explicitly')
    horizon_end = _live_horizon(min(horizon_end, source.horizon_end, source.coordinate.valid_until, destination.valid_until), source.clocks)
    timing = PublicationTiming(max(c.known_at for c in clocks), cut, completed_at, horizon_end)
    derived = derived_clocks(clocks, source_version=id, actual_completion_at=completed_at)
    derived = replace(derived, valid_from=max(destination.valid_from, source.coordinate.valid_from,
                      source.clocks.valid_from if source.clocks.valid_from is not None else source.coordinate.valid_from),
                      valid_until=horizon_end)
    output = CoordinateState(id+':destination', destination, source.kind, values, masses, derived,
                             tuple(dict.fromkeys((*source.lineage, *evidence))), horizon_end, (*source.chain, id), mode != 'reset',
                             uncertainty, source.exposure_lineage, source.cost_lineage)
    return TransitionRecord(id, mode, source, output, bridge, timing, reason, operations)


def require_raw_contract_parity(selection, *, book, trades, bars, at):
    if type(selection) is not RollSelection or not selection.available(at): raise DependencyUnavailable('published selection unavailable')
    if any(type(c) is not RawCoordinate or c != selection.coordinate for c in (book, trades, bars)):
        raise ContractError('book/trades/bars differ from the selected raw contract coordinate')
    return selection.version


def require_executable_level(state, *, at):
    if type(state) is not CoordinateState or not state.available(at) or state.kind != 'level':
        raise DependencyUnavailable('active published level required')
    if not state.on_grid: raise ContractError('off-grid mapped level needs a separately declared rounding/risk policy')
    return state.values[0]


@dataclass(frozen=True)
class EquityAdjustment:
    """Legacy unpublished exact split/display arithmetic, not a dividend model."""
    id: str
    asset: str
    effective_at: int
    known_at: int
    factor: Fraction
    source_version: str

    def __post_init__(self):
        for v in (self.id, self.asset, self.source_version): _name(v)
        timestamp(self.effective_at); timestamp(self.known_at); _fraction(self.factor, positive=True)

    def apply(self, raw_price, *, cut):
        _fraction(raw_price); timestamp(cut)
        if cut < max(self.effective_at, self.known_at): raise DependencyUnavailable('future/unpublished action')
        return {'price': raw_price*self.factor, 'coordinate': 'causally_adjusted_display', 'version': digest(self),
                'published': False, 'input_known_at': self.known_at, 'effective_at': self.effective_at}


@dataclass(frozen=True)
class CorporateAction:
    id: str
    logical_id: str
    asset: RawCoordinate
    kind: str
    effective_at: int
    clocks: Clocks
    factor: Fraction = Fraction(1)
    cash_per_share: Fraction = Fraction(0)
    supersedes: str | None = None

    def __post_init__(self):
        _name(self.id); _name(self.logical_id); timestamp(self.effective_at)
        _fraction(self.factor, positive=True); _fraction(self.cash_per_share, nonnegative=True)
        if type(self.asset) is not RawCoordinate or type(self.clocks) is not Clocks or self.kind not in ('split', 'dividend'):
            raise ContractError('typed exact split or cash-dividend evidence required')
        if self.kind == 'split' and self.cash_per_share != 0 or self.kind == 'dividend' and self.factor != 1:
            raise ContractError('split scaling and cash dividend are different adjustment domains')
        if self.supersedes is not None: _name(self.supersedes)

    @property
    def version(self): return digest(self)
    @property
    def known_at(self): return self.clocks.known_at


@dataclass(frozen=True)
class AdjustmentResult:
    id: str
    action: CorporateAction
    observations: tuple[PriceObservation, ...]
    coordinate: str
    values: tuple[tuple[str, Fraction], ...]
    timing: PublicationTiming
    quantity: Fraction
    requested_horizon_end: int

    def __post_init__(self):
        _name(self.id); _fraction(self.quantity, positive=True); timestamp(self.requested_horizon_end)
        if type(self.action) is not CorporateAction or type(self.timing) is not PublicationTiming:
            raise ContractError('typed action/result input evidence required')
        if type(self.values) is not tuple or any(type(p) is not tuple or len(p) != 2 for p in self.values):
            raise ContractError('immutable adjusted output fields required')
        for key, value in self.values: _name(key); _fraction(value)
        expected = _action_components(action=self.action, observations=self.observations, quantity=self.quantity,
            cut=self.timing.decision_cut, completed_at=self.timing.actual_completion_at, horizon_end=self.requested_horizon_end)
        if (self.coordinate, self.values, self.timing) != expected:
            raise IntegrityError('adjustment differs from its retained raw transformation inputs')

    @property
    def version(self): return digest(self)
    @property
    def known_at(self): return self.timing.known_at
    def available(self, at): return self.timing.available(at) and self.action.asset.available(at)
    def value(self, key): return dict(self.values)[key]


def _action_components(*, action, observations, cut, completed_at, horizon_end, quantity):
    _fraction(quantity, positive=True)
    if type(action) is not CorporateAction or type(observations) is not tuple or not observations or any(type(o) is not PriceObservation for o in observations):
        raise ContractError('action transforms original raw observations, never adjusted output')
    if action.effective_at > cut or not action.clocks.available(cut) or not action.asset.available(cut):
        raise DependencyUnavailable('action unavailable/not effective at decision cut')
    # Observed prices are historical inputs, but an explicitly finite evidence
    # validity remains a live-use limit. historical_available is audit-only.
    if any(o.coordinate != action.asset or not o.available(cut) for o in observations):
        raise DependencyUnavailable('raw action inputs unavailable or wrong coordinate')
    horizon_end = _live_horizon(min(horizon_end, action.asset.valid_until), action.clocks, *(o.clocks for o in observations))
    timing = PublicationTiming(max(action.known_at, *(o.clocks.known_at for o in observations)), cut, completed_at, horizon_end)
    if action.kind == 'split':
        if len(observations) != 1 or observations[0].observed_at >= action.effective_at:
            raise ContractError('split display reference requires a pre-effect raw price')
        p = observations[0].price
        values = (('price', p*action.factor), ('quantity', quantity/action.factor), ('notional', p*quantity))
        coordinate = 'split_adjusted_display'
    else:
        if len(observations) != 2 or not observations[0].observed_at < action.effective_at <= observations[1].observed_at:
            raise ContractError('cash dividend reference needs pre/ex-effect raw prices')
        change = observations[1].price-observations[0].price
        values = (('raw_point_change', change), ('total_return_cash_change', change+action.cash_per_share))
        coordinate = 'total_return_cash_change'
    return coordinate, values, timing


def apply_action(*, id, action, observations, cut, completed_at, horizon_end, quantity=Fraction(1)):
    coordinate, values, timing = _action_components(action=action, observations=observations, cut=cut,
        completed_at=completed_at, horizon_end=horizon_end, quantity=quantity)
    return AdjustmentResult(id, action, observations, coordinate, values, timing, quantity, horizon_end)


def require_raw_option_coordinate(underlying_coordinate, strike_coordinate):
    if underlying_coordinate != 'raw' or strike_coordinate != 'raw':
        raise ContractError('raw strikes cannot use adjusted display/total-return underlying coordinates')


def require_option_underlying(observation, *, expected, at):
    if type(observation) is not PriceObservation or type(expected) is not RawCoordinate:
        raise ContractError('option underlier must be typed original raw price, not an adjusted result')
    if observation.coordinate != expected or not observation.available(at):
        raise DependencyUnavailable('wrong/unavailable exact option underlying coordinate')
    return observation.version


@dataclass(frozen=True)
class RawFill:
    id: str
    coordinate: RawCoordinate
    price: Fraction
    side: int
    contracts: int
    at: int
    fee: Fraction

    def __post_init__(self):
        _name(self.id); timestamp(self.at); _fraction(self.price); _fraction(self.fee, nonnegative=True)
        _integer(self.contracts, minimum=1)
        if type(self.coordinate) is not RawCoordinate or type(self.side) is not int or self.side not in (-1, 1): raise ContractError('raw fill coordinate and side required')
        if not self.coordinate.available(self.at) or (self.price/self.coordinate.tick_size).denominator != 1:
            raise ContractError('raw fill violates lifetime/tick grid')


def raw_fill_pnl(legs):
    if type(legs) is not tuple or not legs: raise ContractError('immutable nonempty raw fill legs required')
    seen = set(); gross = Fraction(0); fees = Fraction(0); currency = None
    for leg in legs:
        if type(leg) is not tuple or len(leg) != 2 or any(type(f) is not RawFill for f in leg): raise ContractError('entry/exit raw fill pairs required')
        entry, exit = leg
        if currency is None: currency = entry.coordinate.currency
        if entry.coordinate.currency != currency or exit.coordinate.currency != currency:
            raise ContractError('raw fill cash legs cannot mix currencies without an explicit conversion')
        if entry.coordinate != exit.coordinate or entry.side != -exit.side or entry.contracts != exit.contracts or exit.at < entry.at:
            raise ContractError('raw contract/side/quantity/time mismatch within fill leg')
        if entry.id == exit.id or entry.id in seen or exit.id in seen: raise ContractError('duplicate actual fill evidence')
        seen.update((entry.id, exit.id))
        gross += entry.side*(exit.price-entry.price)*entry.coordinate.multiplier*entry.contracts
        fees += entry.fee+exit.fee
    return {'gross': gross, 'fees': fees, 'net': gross-fees, 'currency': currency, 'fill_ids': tuple(sorted(seen))}


_RECORD_TYPES = {c.__name__: c for c in (ContractUniverse, SessionVolume, SessionSequence, Session, Clocks, InstrumentKey, InstrumentDefinition,
    RawCoordinate, PublicationTiming, RollPolicy, ContractMap, RollSelection, PriceObservation, BridgePolicy,
    RollBridge, CoordinateState, RollLimits, TransitionRecord, CorporateAction, AdjustmentResult)}
_TOP_TYPES = (ContractMap, RollSelection, RollBridge, CoordinateState, TransitionRecord, CorporateAction, AdjustmentResult)


def _pack(value):
    if type(value) is Fraction: return {'fraction': [value.numerator, value.denominator]}
    if type(value) is Decimal and value.is_finite(): return {'decimal': str(value)}
    if type(value) is AvailabilityBasis: return {'basis': value.value}
    # Session civil dates are immutable calendar metadata, never a guessed timestamp.
    from datetime import date
    if type(value) is date: return {'date': value.isoformat()}
    if type(value) is tuple: return {'tuple': [_pack(v) for v in value]}
    if is_dataclass(value) and type(value).__name__ in _RECORD_TYPES:
        return {'type': type(value).__name__, 'fields': {f.name: _pack(getattr(value, f.name)) for f in fields(value)}}
    if value is None or type(value) in (str, int, bool): return value
    raise ContractError('unsupported mutable/nonexact roll envelope value')


def _unpack(value):
    from datetime import date
    if value is None or type(value) in (str, int, bool): return value
    if type(value) is not dict: raise ContractError('invalid roll envelope encoding')
    if set(value) == {'fraction'}:
        n, d = value['fraction']; _integer(d, minimum=1)
        if type(n) is not int: raise ContractError('invalid rational numerator')
        return Fraction(n, d)
    if set(value) == {'decimal'}:
        result = Decimal(value['decimal'])
        if not result.is_finite(): raise ContractError('nonfinite decimal in retained definition')
        return result
    if set(value) == {'basis'}: return AvailabilityBasis(value['basis'])
    if set(value) == {'date'}: return date.fromisoformat(value['date'])
    if set(value) == {'tuple'}: return tuple(_unpack(v) for v in value['tuple'])
    if set(value) == {'type', 'fields'} and value['type'] in _RECORD_TYPES:
        return _RECORD_TYPES[value['type']](**{k: _unpack(v) for k, v in value['fields'].items()})
    raise ContractError('unknown roll envelope type')


class RollLedger:
    """Bounded F08 records in the existing durable journal; no market cohort claim."""
    def __init__(self, journal: Journal, *, limits=RollLimits()):
        if type(journal) is not Journal or type(limits) is not RollLimits: raise ContractError('typed journal and frozen roll limits required')
        self._journal, self._limits, self._lock = journal, limits, RLock()
        config = {'schema': 'f08-coordinate-ledger-v1', 'limits': _pack(limits)}
        journal.append(key='f08-contract', kind='f08_contract', payload=config)
        self._reload()

    @property
    def journal(self): return self._journal

    @property
    def limits(self): return self._limits

    def _reload(self):
        self._records, self._states, self._consumed, self._bytes = {}, {}, {}, 0
        self._object_ids = {}
        events = self.journal.read()
        self._head = events[-1]['hash'] if events else None
        for event in events:
            if event['kind'] == 'f08_contract':
                if event['payload'] != {'schema': 'f08-coordinate-ledger-v1', 'limits': _pack(self.limits)}:
                    raise IntegrityError('roll ledger configuration changed')
            if event['kind'] != 'f08_record': continue
            p = event['payload']
            try: record = _unpack(p['record'])
            except (TypeError, KeyError, ValueError) as exc: raise IntegrityError('invalid typed roll record') from exc
            if type(record) not in _TOP_TYPES or record.version != p['version'] or _pack(record) != p['record']:
                raise IntegrityError('roll record content/version changed')
            if record.id in self._records: raise IntegrityError('duplicate roll record ID')
            self._validate(record)
            self._check_bounds(1, len(canonical_json(p)))
            self._accept(record, len(canonical_json(p)))
        self._check_bounds(0, 0)

    def _check_bounds(self, count, size):
        if len(self._records)+count > self.limits.max_records or self._bytes+size > self.limits.max_bytes:
            raise ContractError('retained F08 envelope bound reached; explicit archive/rotation required')

    @staticmethod
    def _identity_claims(record):
        claims = [(record.id, type(record).__name__, record.version)]
        if type(record) is TransitionRecord:
            claims.append((record.destination.id, 'CoordinateState', record.destination.version))
        return tuple(claims)

    def _validate(self, record):
        if type(record) not in _TOP_TYPES: raise ContractError('unsupported typed roll ledger record')
        local = {}
        for id, role, version in self._identity_claims(record):
            claim = (role, version)
            if id in local and local[id] != claim or id in self._object_ids and self._object_ids[id] != claim:
                raise IntegrityError('top-level or nested coordinate identity reused with different content/role')
            local[id] = claim
        if type(record) in (RollSelection, AdjustmentResult):
            record.__post_init__()
        if type(record) is CoordinateState:
            if record.chain: raise ContractError('derived state must arrive through its committed transition')
            if len(record.values) > self.limits.max_profile_nodes: raise ContractError('profile node bound exceeded')
        elif type(record) is TransitionRecord:
            source = self._states.get(record.source.version)
            if source != record.source: raise ContractError('transition requires the actually registered source state version')
            if source.version in self._consumed: raise ContractError('source state already transitioned; use the destination version')
            expected = transition_state(id=record.id, source=source, destination=record.destination.coordinate,
                mode=record.mode, cut=record.timing.decision_cut, completed_at=record.timing.actual_completion_at,
                horizon_end=record.timing.horizon_end, reason=record.reason, bridge=record.bridge, limits=self.limits)
            if expected != record: raise IntegrityError('transition output differs from its frozen source/evidence')
            if record.bridge is not None and self._records.get(record.bridge.id) != record.bridge:
                raise ContractError('transition bridge was not durably registered')
        elif type(record) is CorporateAction:
            chain = [r for r in self._records.values() if type(r) is CorporateAction and r.logical_id == record.logical_id]
            if len(chain)+1 > self.limits.max_chain:
                raise ContractError('corporate action revision chain bound exceeded')
            if not chain:
                if record.supersedes is not None: raise ContractError('corporate revision has no registered logical root')
            else:
                parent = chain[-1]
                if ((parent.asset, parent.kind) != (record.asset, record.kind)
                        or record.supersedes != parent.version or parent.known_at >= record.known_at):
                    raise ContractError('logical action requires one asset/kind and its immediate preceding version')
        elif type(record) is AdjustmentResult:
            if self._records.get(record.action.id) != record.action: raise ContractError('adjusted result needs registered action evidence')

    def _accept(self, record, size):
        self._records[record.id] = record; self._bytes += size
        for id, role, version in self._identity_claims(record): self._object_ids[id] = (role, version)
        if type(record) is CoordinateState: self._states[record.version] = record
        if type(record) is TransitionRecord:
            self._states[record.destination.version] = record.destination
            self._consumed[record.source.version] = record.id

    def append(self, record):
        with self._lock:
            self._reload()
            if type(record) not in _TOP_TYPES: raise ContractError('typed roll ledger record required')
            old = self._records.get(record.id)
            if old is not None:
                if old != record: raise IntegrityError('roll evidence ID reused with different content')
                return False
            self._validate(record)
            p = {'version': record.version, 'record': _pack(record)}
            size = len(canonical_json(p)); self._check_bounds(1, size)
            self.journal.append(key='f08:'+record.id, kind='f08_record', payload=p,
                                expected_head=self._head, check_head=True)
            self._accept(record, size)
            return True

    def state(self, version, *, at):
        timestamp(at)
        with self._lock:
            self._reload(); result = self._states.get(version)
            if result is None or not result.available(at): return None
            transition_id = self._consumed.get(version)
            if transition_id is not None and self._records[transition_id].known_at <= at: return None
            return result

    def bridge_at(self, old, new, *, at):
        timestamp(at)
        with self._lock:
            self._reload()
            rows = [r for r in self._records.values() if type(r) is RollBridge and r.old.coordinate == old
                    and r.new.coordinate == new and r.known_at <= at]
            if not rows: return None
            latest = max(r.known_at for r in rows); rows = [r for r in rows if r.known_at == latest]
            if len(rows) != 1: raise ContractError('ambiguous same-time roll bridge')
            return rows[0] if rows[0].available(at) else None

    def action_at(self, logical_id, *, at):
        _name(logical_id); timestamp(at)
        with self._lock:
            self._reload(); rows = [r for r in self._records.values() if type(r) is CorporateAction and r.logical_id == logical_id and r.known_at <= at]
            if not rows: return None
            latest = max(r.known_at for r in rows); rows = [r for r in rows if r.known_at == latest]
            if len(rows) != 1: raise ContractError('ambiguous same-time corporate action')
            return rows[0] if rows[0].effective_at <= at and rows[0].clocks.available(at) and rows[0].asset.available(at) else None

    def metrics(self):
        with self._lock:
            self._reload()
            return {'retained_records': len(self._records), 'retained_envelope_bytes': self._bytes,
                    'max_records': self.limits.max_records, 'max_bytes': self.limits.max_bytes}

    def record(self, id, *, at):
        """A record's input-known clock never grants early output publication."""
        _name(id); timestamp(at)
        with self._lock:
            self._reload(); row = self._records.get(id)
            if row is None: return None
            if type(row) is ContractMap:
                return row if row.clocks.available(at) and row.effective_at <= at < row.valid_until else None
            if type(row) is CorporateAction:
                return row if row.clocks.available(at) else None
            return row if row.available(at) else None
