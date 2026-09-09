"""Definition-bound exact units and conditional exercise obligations (F02).

These kernels price no time value and send no orders. A physical exercise
obligation is distinct from current cash, intrinsic value and a later fill.
"""

from dataclasses import dataclass
from fractions import Fraction
import re

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.time import Clocks, timestamp
from trading_research.operations.artifacts import digest


def exact(value, name='value'):
    if not isinstance(value, Fraction):
        raise ContractError(f'{name} must be an exact rational')
    return value


def currency(value):
    if not isinstance(value, str) or not re.fullmatch('[A-Z]{3}', value):
        raise ContractError('explicit three-letter cash currency required')
    return value


def named(value, name='identity'):
    if not isinstance(value, str) or not value:
        raise ContractError(f'explicit immutable {name} text required')
    return value


def ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


@dataclass(frozen=True)
class PriceDomain:
    lower: Fraction | None
    upper: Fraction | None = None

    def __post_init__(self):
        for bound in (self.lower, self.upper):
            if bound is not None:
                exact(bound, 'price-domain bound')
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ContractError('empty price domain')

    def require(self, value: Fraction):
        exact(value)
        if self.lower is not None and value < self.lower or self.upper is not None and value > self.upper:
            raise DependencyUnavailable('price is outside this contract/model domain')
        return value


@dataclass(frozen=True)
class TickBand:
    lower: Fraction | None
    upper: Fraction | None
    step: Fraction
    origin: Fraction = Fraction(0)

    def __post_init__(self):
        PriceDomain(self.lower, self.upper)
        if exact(self.step) <= 0 or self.lower is not None and self.lower == self.upper:
            raise ContractError('tick bands must have positive extent and increment')
        exact(self.origin)

    def contains(self, value):
        return (self.lower is None or self.lower <= value) and (self.upper is None or value < self.upper)


@dataclass(frozen=True)
class TickSchedule:
    id: str
    domain: PriceDomain
    bands: tuple[TickBand, ...]

    def __post_init__(self):
        named(self.id, 'tick schedule source')
        if (not isinstance(self.domain, PriceDomain) or not isinstance(self.bands, tuple)
                or not 1 <= len(self.bands) <= 64 or any(not isinstance(b, TickBand) for b in self.bands)):
            raise ContractError('bounded immutable tick bands and source identity required')
        if self.bands[0].lower != self.domain.lower or self.bands[-1].upper is not None:
            raise ContractError('tick bands must cover the declared domain')
        for left, right in zip(self.bands, self.bands[1:]):
            if left.upper is None or right.lower is None or left.upper != right.lower:
                raise ContractError('tick bands have a gap, overlap or invalid ordering')
        if self.domain.upper is not None and any(b.lower is not None and b.lower > self.domain.upper for b in self.bands):
            raise ContractError('tick bands outside the price domain are not applicable contract terms')

    def band(self, value):
        self.domain.require(value)
        return next(b for b in self.bands if b.contains(value))

    def require(self, value):
        band = self.band(value)
        if ((value - band.origin) / band.step).denominator != 1:
            raise ContractError('price is not on its applicable tick grid')
        return value

    def rounded(self, value, *, direction: str):
        self.domain.require(value)
        if direction not in ('floor', 'ceil'):
            raise ContractError('rounding direction must be explicit')
        candidates = []
        for band in self.bands:
            bound = value
            if direction == 'floor':
                index = ((bound - band.origin) / band.step).__floor__()
                if band.upper is not None:
                    index = min(index, ceil((band.upper - band.origin) / band.step) - 1)
                candidate = band.origin + index * band.step
            else:
                if band.lower is not None:
                    bound = max(bound, band.lower)
                candidate = band.origin + ceil((bound - band.origin) / band.step) * band.step
            if band.contains(candidate) and (self.domain.upper is None or candidate <= self.domain.upper):
                if direction == 'floor' and candidate <= value or direction == 'ceil' and candidate >= value:
                    candidates.append(candidate)
        if not candidates:
            raise DependencyUnavailable('no valid grid point in the requested direction')
        return max(candidates) if direction == 'floor' else min(candidates)


@dataclass(frozen=True)
class Cash:
    amount: Fraction
    currency: str

    def __post_init__(self):
        exact(self.amount)
        currency(self.currency)


@dataclass(frozen=True)
class FxRate:
    base: str
    quote: str
    quote_per_base: Fraction
    clocks: Clocks

    def __post_init__(self):
        currency(self.base)
        currency(self.quote)
        if not isinstance(self.clocks, Clocks) or self.clocks.valid_from is None or self.clocks.valid_until is None:
            raise ContractError('FX conversion requires an explicit available validity interval')
        if self.base == self.quote or exact(self.quote_per_base) <= 0:
            raise ContractError('FX conversion needs distinct currencies and a positive exact rate')

    def convert(self, cash: Cash, *, cut: int):
        if not isinstance(cash, Cash):
            raise ContractError('FX conversion requires typed exact cash')
        if cash.currency != self.base or not self.clocks.available(cut):
            raise DependencyUnavailable('FX currency or availability does not match')
        return Cash(cash.amount * self.quote_per_base, self.quote)


@dataclass(frozen=True)
class ContractCalendar:
    last_trade_at: int
    exercise_start_at: int
    exercise_end_at: int
    fixing_at: int
    payment_at: int
    source_version: str

    def __post_init__(self):
        named(self.source_version, 'calendar source version')
        for value in (self.last_trade_at, self.exercise_start_at, self.exercise_end_at, self.fixing_at, self.payment_at):
            timestamp(value)
        if (not self.source_version or not self.exercise_start_at <= self.fixing_at <= self.exercise_end_at
                or self.last_trade_at > self.exercise_end_at or self.payment_at < self.exercise_end_at):
            raise ContractError('separate ordered trading, exercise, fixing and payment clocks required')


@dataclass(frozen=True)
class Deliverable:
    asset_identity: str
    quantity: Fraction
    price_unit: str
    price_currency: str | None = None

    def __post_init__(self):
        named(self.asset_identity)
        named(self.price_unit, 'deliverable price unit')
        currency(self.price_currency)
        if exact(self.quantity) <= 0:
            raise ContractError('known deliverable asset, unit and positive exact quantity required')


@dataclass(frozen=True)
class PriceObservation:
    identity: str
    price_unit: str
    value: Fraction
    clocks: Clocks
    price_currency: str | None = None

    def __post_init__(self):
        named(self.identity)
        named(self.price_unit, 'observed price unit')
        if not isinstance(self.clocks, Clocks) or self.clocks.event_at is None:
            raise ContractError('observed price requires its exact coordinate, unit and event clock')
        if self.price_currency is not None:
            currency(self.price_currency)
        exact(self.value)

    @property
    def version(self):
        return digest(self)


@dataclass(frozen=True)
class PayoffTerms:
    id: str
    definition_version: str
    kind: str
    currency: str
    quote_unit: str
    quote_multiplier: Fraction
    underlying_root: str
    underlying_identity: str
    underlying_price_unit: str
    underlying_domain: PriceDomain
    ticks: TickSchedule
    calendar: ContractCalendar
    clocks: Clocks
    fixing_identity: str | None = None
    strike: Fraction | None = None
    right: str | None = None
    exercise: str | None = None
    deliverables: tuple[Deliverable, ...] = ()
    deliverable_cash: Fraction = Fraction(0)
    exercise_cash: Fraction | None = None
    deliverable_complete: bool = True
    unsupported_reason: str | None = None

    def __post_init__(self):
        for value in (self.id, self.definition_version, self.kind, self.quote_unit, self.underlying_root,
                      self.underlying_identity, self.underlying_price_unit):
            named(value, 'definition-bound terms or price coordinate')
        if (not isinstance(self.underlying_domain, PriceDomain) or not isinstance(self.ticks, TickSchedule)
                or not isinstance(self.calendar, ContractCalendar) or not isinstance(self.clocks, Clocks)
                or self.clocks.valid_from is None or self.clocks.valid_until is None):
            raise ContractError('typed domain, tick schedule, calendar and bounded validity required')
        if self.unsupported_reason is not None:
            named(self.unsupported_reason, 'unsupported reason')
        currency(self.currency)
        if exact(self.quote_multiplier) <= 0:
            raise ContractError('positive quote/cash multiplier required')
        if self.kind not in ('linear_future', 'cash_index_option', 'physical_equity_option', 'physical_future_option'):
            raise DependencyUnavailable('unsupported payoff adapter; no default style')
        if (not isinstance(self.deliverables, tuple) or len(self.deliverables) > 64
                or any(not isinstance(d, Deliverable) for d in self.deliverables)
                or len({d.asset_identity for d in self.deliverables}) != len(self.deliverables)):
            raise ContractError('immutable distinct deliverable identities required')
        exact(self.deliverable_cash)
        if type(self.deliverable_complete) is not bool:
            raise ContractError('deliverable completeness must be explicit')
        if self.kind != 'linear_future':
            if self.right not in ('C', 'P') or self.exercise not in ('american', 'european'):
                raise DependencyUnavailable('unsupported or missing option right/exercise style')
            exact(self.strike, 'option strike')
            named(self.fixing_identity, 'expiration fixing identity')
        elif any(v is not None for v in (self.strike, self.right, self.exercise, self.fixing_identity)):
            raise ContractError('linear future cannot carry an option payoff')
        if self.kind == 'physical_equity_option':
            if not self.deliverables or self.exercise_cash is None:
                raise DependencyUnavailable('physical option deliverable/exercise cash incomplete')
            if exact(self.exercise_cash) < 0 or any(d.price_currency != self.currency for d in self.deliverables):
                raise ContractError('basket cash and prices need one explicit currency and nonnegative exercise cash')
        elif self.deliverables or self.deliverable_cash or self.exercise_cash is not None:
            raise ContractError('basket fields are specific to physical equity deliverables')


@dataclass(frozen=True)
class PositionDelivery:
    asset_identity: str
    quantity: Fraction
    exercise_basis: Fraction | None

    def __post_init__(self):
        named(self.asset_identity)
        if not exact(self.quantity):
            raise ContractError('a position delivery must have a nonzero exact quantity')
        if self.exercise_basis is not None:
            exact(self.exercise_basis)


@dataclass(frozen=True)
class ExerciseObligation:
    kernel_version: str
    intrinsic: Cash
    cash_transfer: Cash
    positions: tuple[PositionDelivery, ...]
    observed_at: int
    known_at: int
    cash_due_at: int
    input_versions: tuple[str, ...]
    interpretation: str = 'conditional exercise if positive intrinsic; not an assignment or received cash'

    def __post_init__(self):
        named(self.kernel_version, 'kernel version')
        if (not isinstance(self.intrinsic, Cash) or not isinstance(self.cash_transfer, Cash)
                or self.intrinsic.amount < 0 or self.intrinsic.currency != self.cash_transfer.currency
                or not isinstance(self.positions, tuple) or any(not isinstance(p, PositionDelivery) for p in self.positions)
                or not isinstance(self.input_versions, tuple) or not self.input_versions
                or any(not isinstance(v, str) or not v for v in self.input_versions)):
            raise ContractError('typed immutable obligations, consistent currency and source versions required')
        for value in (self.observed_at, self.known_at, self.cash_due_at):
            timestamp(value)
        if self.known_at < self.observed_at or self.cash_due_at < self.observed_at:
            raise ContractError('obligation knowledge/payment cannot precede its exercise observation')


@dataclass(frozen=True)
class PayoffKernel:
    definition: InstrumentDefinition
    terms: PayoffTerms
    underlying_definition: InstrumentDefinition | None
    compiled_valid_at: int
    compiled_known_at: int

    def __post_init__(self):
        _validate_payoff_inputs(self.definition, self.terms, valid_at=self.compiled_valid_at,
                               known_at=self.compiled_known_at, underlying_definition=self.underlying_definition)

    @property
    def version(self):
        return digest(self)

    @property
    def known_at(self):
        return max(self.definition.clocks.known_at, self.terms.clocks.known_at,
                   self.underlying_definition.clocks.known_at if self.underlying_definition else self.definition.clocks.known_at)

    def can_trade(self, *, cut: int):
        """Calendar/terms check only; current registry, account and order gates remain required."""
        return (self.definition.clocks.available(cut) and self.terms.clocks.available(cut)
                and (self.underlying_definition is None or self.underlying_definition.clocks.available(cut))
                and self.known_at <= cut < min(self.terms.calendar.last_trade_at, self.definition.key.expiry_at))

    def premium_cash(self, price: Fraction):
        self.terms.ticks.require(price)
        return Cash(price * self.terms.quote_multiplier, self.terms.currency)

    def linear_pnl(self, entry: Fraction, exit: Fraction, *, side: int = 1):
        if self.terms.kind != 'linear_future' or type(side) is not int or side not in (-1, 1):
            raise ContractError('one-contract linear futures P&L requires its adapter and direction')
        self.terms.ticks.require(entry)
        self.terms.ticks.require(exit)
        return Cash((exit - entry) * side * self.terms.quote_multiplier, self.terms.currency)

    def _inputs(self, observations, *, at, cut, maximum_age_ns, fixing):
        timestamp(at)
        timestamp(cut)
        if type(maximum_age_ns) is not int or maximum_age_ns < 0 or self.known_at > cut or at > cut:
            raise DependencyUnavailable('payoff inputs unavailable at the requested cut')
        if (not isinstance(observations, tuple) or any(not isinstance(o, PriceObservation) for o in observations)
                or len({o.identity for o in observations}) != len(observations)):
            raise ContractError('immutable unique price observations required')
        terms = self.terms
        if (not self.definition.clocks.available(cut, valid_at=at) or not terms.clocks.available(cut, valid_at=at)
                or at > self.definition.key.expiry_at
                or self.underlying_definition is not None and not self.underlying_definition.clocks.available(cut, valid_at=at)):
            raise DependencyUnavailable('contract inputs do not apply at this effective payoff time')
        expected = ({d.asset_identity: (d.price_unit, d.price_currency) for d in terms.deliverables}
                    if terms.kind == 'physical_equity_option'
                    else {terms.fixing_identity if fixing else terms.underlying_identity: (terms.underlying_price_unit, None)})
        if {o.identity for o in observations} != set(expected):
            raise DependencyUnavailable('missing, wrong or extra payoff price coordinate')
        for observation in observations:
            if ((observation.price_unit, observation.price_currency) != expected[observation.identity]
                    or not observation.clocks.available(cut, valid_at=at)
                    or observation.clocks.event_at > at
                    or at - observation.clocks.event_at > maximum_age_ns
                    or fixing and observation.clocks.event_at != at):
                raise DependencyUnavailable('price unit, age, fixing time or availability mismatch')
            terms.underlying_domain.require(observation.value)
        return {o.identity: o.value for o in observations}

    def _intrinsic(self, values, *, fixing):
        terms = self.terms
        sign = 1 if terms.right == 'C' else -1
        if terms.kind == 'physical_equity_option':
            gross = sum((d.quantity * values[d.asset_identity] for d in terms.deliverables), terms.deliverable_cash)
            signed = sign * (gross - terms.exercise_cash)
        else:
            value = values[terms.fixing_identity if fixing else terms.underlying_identity]
            signed = sign * (value - terms.strike) * terms.quote_multiplier
        return Cash(max(Fraction(0), signed), terms.currency)

    def intrinsic(self, observations: tuple[PriceObservation, ...], *, at: int, cut: int, maximum_age_ns: int):
        if self.terms.kind == 'linear_future':
            raise ContractError('a future has no option exercise intrinsic')
        values = self._inputs(observations, at=at, cut=cut, maximum_age_ns=maximum_age_ns, fixing=False)
        return self._intrinsic(values, fixing=False)

    def exercise_obligation(self, observations: tuple[PriceObservation, ...], *, at: int, cut: int, maximum_age_ns: int = 0):
        terms = self.terms
        calendar = terms.calendar
        if terms.kind == 'linear_future':
            raise ContractError('linear futures use cash variation, not option exercise')
        if (not calendar.exercise_start_at <= at <= calendar.exercise_end_at
                or terms.exercise == 'european' and at != calendar.fixing_at):
            raise DependencyUnavailable('exercise outside the explicit contract window')
        if at != calendar.fixing_at:
            raise DependencyUnavailable('early exercise settlement requires a separately supplied payment schedule')
        fixing = at == calendar.fixing_at
        values = self._inputs(observations, at=at, cut=cut, maximum_age_ns=maximum_age_ns, fixing=fixing)
        intrinsic = self._intrinsic(values, fixing=fixing)
        transfer = Cash(Fraction(0), terms.currency)
        positions = ()
        sign = 1 if terms.right == 'C' else -1
        if intrinsic.amount > 0:
            if terms.kind == 'cash_index_option':
                transfer = intrinsic
            elif terms.kind == 'physical_equity_option':
                transfer = Cash(sign * (terms.deliverable_cash - terms.exercise_cash), terms.currency)
                positions = tuple(PositionDelivery(d.asset_identity, sign * d.quantity, None) for d in terms.deliverables)
            elif terms.kind == 'physical_future_option':
                positions = (PositionDelivery(terms.underlying_identity, Fraction(sign), terms.strike),)
        return ExerciseObligation(self.version, intrinsic, transfer, positions, at,
                                  max(at, self.known_at, *(o.clocks.known_at for o in observations)),
                                  calendar.payment_at, tuple(sorted(o.version for o in observations)))

    def quote_sensitivity_cash(self, derivative: Fraction, *, quote_unit: str, with_respect_to: str):
        named(with_respect_to, 'sensitivity denominator unit')
        if quote_unit != self.terms.quote_unit:
            raise ContractError('sensitivity numerator and denominator units must be explicit')
        return {'value': exact(derivative) * self.terms.quote_multiplier,
                'numerator_unit': self.terms.currency, 'denominator_unit': with_respect_to,
                'kernel_version': self.version}


def _validate_payoff_inputs(definition: InstrumentDefinition, terms: PayoffTerms, *, valid_at: int, known_at: int,
                           underlying_definition: InstrumentDefinition | None = None):
    timestamp(valid_at)
    timestamp(known_at)
    if valid_at > known_at:
        raise ContractError('compilation cannot claim a future effective observation cut')
    if (not isinstance(definition, InstrumentDefinition) or not isinstance(terms, PayoffTerms)
            or underlying_definition is not None and not isinstance(underlying_definition, InstrumentDefinition)):
        raise ContractError('typed immutable payoff compilation inputs required')
    if (not definition.clocks.available(known_at, valid_at=valid_at)
            or not terms.clocks.available(known_at, valid_at=valid_at)):
        raise DependencyUnavailable('future or out-of-validity contract definition/terms')
    if terms.unsupported_reason or not terms.deliverable_complete or not definition.eligibility('execution')[0]:
        raise DependencyUnavailable(terms.unsupported_reason or 'incomplete or unsupported deliverable')
    if (definition.key.definition_version != terms.definition_version
            or definition.key.underlying != terms.underlying_root
            or definition.multiplier is None or Fraction(definition.multiplier) != terms.quote_multiplier):
        raise ContractError('kernel identity, underlier root or multiplier disagrees with the definition')
    if definition.key.expiry_at is None or valid_at >= definition.key.expiry_at:
        raise DependencyUnavailable('payoff compilation requires a known unexpired contract')
    if (Fraction(definition.tick_size) != min(b.step for b in terms.ticks.bands)
            or terms.calendar.last_trade_at > definition.key.expiry_at):
        raise ContractError('tick schedule or last-trade deadline disagrees with the definition')
    if terms.kind == 'linear_future':
        if definition.classification != 'future' or terms.underlying_identity != instrument_identity(definition):
            raise ContractError('linear kernel requires this exact outright future')
        if terms.quote_unit != terms.underlying_price_unit:
            raise ContractError('linear entry and exit prices must use the same points coordinate')
        if definition.key.underlying in ('NQ', 'ES') and (len(terms.ticks.bands) != 1
                or (terms.ticks.bands[0].origin / terms.ticks.bands[0].step).denominator != 1):
            raise ContractError('NQ/ES reference conversion requires its constant zero-origin tick grid')
    else:
        settlement = {'cash_index_option': 'cash', 'physical_equity_option': 'equity', 'physical_future_option': 'future'}[terms.kind]
        if (definition.classification != 'option' or definition.key.strike is None
                or Fraction(definition.key.strike) != terms.strike or definition.key.right != terms.right
                or definition.key.exercise != terms.exercise or definition.key.settlement != settlement
                or definition.key.expiry_at != terms.calendar.exercise_end_at):
            raise ContractError('option strike, right, style, settlement or exact expiry disagrees')
    if terms.kind == 'physical_future_option':
        underlier = underlying_definition
        if (underlier is None or underlier.classification != 'future' or not underlier.eligibility('valuation')[0]
                or definition.underlying_future_id != underlier.key.instrument_id
                or terms.underlying_identity != instrument_identity(underlier)
                or underlier.key.underlying != terms.underlying_root
                or underlier.multiplier is None or Fraction(underlier.multiplier) != terms.quote_multiplier
                or not underlier.clocks.available(known_at, valid_at=valid_at)
                or underlier.key.expiry_at is None or underlier.key.expiry_at < terms.calendar.fixing_at):
            raise DependencyUnavailable('missing, wrong, unavailable or prematurely expired underlying future')
    elif underlying_definition is not None:
        raise ContractError('unexpected underlying-future definition for this payoff kind')


def compile_payoff(definition: InstrumentDefinition, terms: PayoffTerms, *, valid_at: int, known_at: int,
                   underlying_definition: InstrumentDefinition | None = None) -> PayoffKernel:
    return PayoffKernel(definition, terms, underlying_definition, valid_at, known_at)


def literal_option_payoff(*, right: str, strike: Fraction, multiplier: Fraction,
                          underlying: Fraction | None = None, basket: tuple[tuple[Fraction, Fraction], ...] | None = None,
                          deliverable_cash: Fraction = Fraction(0), exercise_cash: Fraction | None = None):
    """Independent direct expiration equation; no compiled constants or market joins."""
    if right not in ('C', 'P'):
        raise ContractError('literal reference right required')
    exact(strike)
    if exact(multiplier) <= 0:
        raise ContractError('literal reference requires a positive multiplier')
    if basket is None:
        value = (exact(underlying) - exact(strike)) * exact(multiplier)
    else:
        if (not isinstance(basket, tuple) or not 1 <= len(basket) <= 64 or underlying is not None
                or any(not isinstance(leg, tuple) or len(leg) != 2 for leg in basket)):
            raise ContractError('literal basket requires bounded immutable independent legs')
        value = exact(deliverable_cash) - exact(exercise_cash)
        for quantity, price in basket:
            if exact(quantity) <= 0:
                raise ContractError('literal physical deliverable quantities must be positive')
            value += exact(quantity) * exact(price)
    return max(Fraction(0), value if right == 'C' else -value)


@dataclass(frozen=True)
class AffineCoordinate:
    source: str
    destination: str
    slope: Fraction
    intercept: Fraction
    known_at: int
    source_version: str
    interpretation: str = 'deterministic_coordinate'

    def __post_init__(self):
        for value in (self.source, self.destination, self.source_version):
            named(value, 'coordinate or source version')
        if not self.source or not self.destination or self.source == self.destination or not self.source_version:
            raise ContractError('explicit distinct coordinates and source version required')
        exact(self.slope)
        exact(self.intercept)
        timestamp(self.known_at)
        if self.interpretation not in ('deterministic_coordinate', 'conditional_mean'):
            raise ContractError('mapping interpretation must be explicit')

    def apply(self, value: Fraction, *, source: str, cut: int):
        if source != self.source or timestamp(cut) < self.known_at:
            raise DependencyUnavailable('mapping coordinate or availability mismatch')
        return self.slope * exact(value) + self.intercept

    def inverse(self):
        if self.interpretation != 'deterministic_coordinate' or self.slope == 0:
            raise DependencyUnavailable('conditional means and singular maps have no reciprocal inverse')
        return AffineCoordinate(self.destination, self.source, 1 / self.slope, -self.intercept / self.slope,
                                self.known_at, digest(self), self.interpretation)


def calendar_time_derivative(remaining_time_derivative: Fraction, *, fixed_expiry: bool):
    if fixed_expiry is not True:
        raise ContractError('calendar/remaining-time derivative sign requires a fixed expiry')
    return -exact(remaining_time_derivative)
