"""Exact arithmetic for units that must never be mixed implicitly (CC-02)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable


class Unit(StrEnum):
    TICKS = "ticks"
    PRICE_POINTS = "price_points"
    CONTRACTS = "contracts"
    SHARES = "shares"
    USD = "USD"
    PREMIUM_USD = "premium_USD"
    LOG_RETURN = "log_return"
    LOG_RETURN_VARIANCE = "log_return_variance"
    TICKS_SQUARED = "ticks_squared"
    ANNUAL_IV_FRACTION = "annual_IV_fraction"
    DELTA_SHARES = "delta_equivalent_shares"
    MINI_EQUIVALENTS = "informational_mini_equivalents"
    GAMMA_USD_PER_ONE_PERCENT = "option_delta_equivalent_USD_per_1pct_move"
    VEGA_USD_PER_UNIT_IV = "USD_per_unit_IV"
    VEGA_USD_PER_VOL_POINT = "USD_per_vol_point"
    PROBABILITY = "probability"
    COUNT = "count"


def exact_decimal(value: str | int | Decimal) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ContractError("use a decimal string/integer, not an implicit binary float")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ContractError("invalid exact decimal") from exc
    if not result.is_finite():
        raise ContractError("nonfinite quantity")
    return result


def _parts(value: Decimal | int) -> tuple[int, int]:
    value = exact_decimal(value)
    sign, digits, exponent = value.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    return -coefficient if sign else coefficient, exponent


def _from_parts(coefficient: int, exponent: int) -> Decimal:
    digits = tuple(int(c) for c in str(abs(coefficient)))
    return Decimal((int(coefficient < 0), digits, exponent))


def decimal_product(*values: Decimal | int) -> Decimal:
    """Finite decimal products without dependence on the caller's Decimal context."""
    coefficient, exponent = 1, 0
    for value in values:
        c, e = _parts(value)
        coefficient *= c
        exponent += e
    return _from_parts(coefficient, exponent)


def decimal_sum(a: Decimal, b: Decimal) -> Decimal:
    ca, ea = _parts(a)
    cb, eb = _parts(b)
    exponent = min(ea, eb)
    return _from_parts(ca * 10 ** (ea - exponent) + cb * 10 ** (eb - exponent), exponent)


@dataclass(frozen=True)
class Quantity:
    value: Decimal
    unit: Unit

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal) or not self.value.is_finite() or not isinstance(self.unit, Unit):
            raise ContractError("quantity requires a finite Decimal and a registered Unit")
        if (self.unit in {Unit.CONTRACTS, Unit.SHARES, Unit.TICKS, Unit.COUNT}
                and self.value != self.value.to_integral_value()):
            raise ContractError(f"{self.unit} must be integral")
        if self.unit == Unit.PROBABILITY and not 0 <= self.value <= 1:
            raise ContractError("probability outside [0,1]")

    def __add__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity) or self.unit != other.unit:
            raise ContractError("incompatible quantity units")
        return Quantity(decimal_sum(self.value, other.value), self.unit)

    def __sub__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity) or self.unit != other.unit:
            raise ContractError("incompatible quantity units")
        return Quantity(decimal_sum(self.value, other.value.copy_negate()), self.unit)


@dataclass(frozen=True, order=True)
class Ticks:
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int:
            raise ContractError("trade/order ticks must be an integer")


@dataclass(frozen=True)
class FuturesTerms:
    root: str
    tick_size: Decimal
    usd_per_point: Decimal
    definition_version: str

    def __post_init__(self) -> None:
        for value in (self.tick_size, self.usd_per_point):
            if not isinstance(value, Decimal) or not value.is_finite() or value <= 0:
                raise ContractError("positive exact futures terms required")
        if not self.root or not self.definition_version:
            raise ContractError("contract terms require identity and version")

    def ticks(self, price: Decimal) -> Ticks:
        price = exact_decimal(price)
        ratio = Fraction(price) / Fraction(self.tick_size)
        if ratio.denominator != 1:
            raise ContractError(f"off-tick price {price}; tick size {self.tick_size}; residual retained in raw payload")
        return Ticks(ratio.numerator)

    def price(self, ticks: Ticks) -> Decimal:
        return decimal_product(self.tick_size, ticks.value)

    def pnl(self, entry: Ticks, exit: Ticks, *, side: int, contracts: int = 1) -> Quantity:
        if type(side) is not int or side not in {-1, 1} or type(contracts) is not int or contracts != 1:
            raise ContractError("primary account requires exactly one outright mini per position")
        return Quantity(decimal_product(exit.value - entry.value, side, self.tick_size, self.usd_per_point), Unit.USD)


# These are arithmetic references, not historical instrument certifications.
NQ_REFERENCE = FuturesTerms("NQ", Decimal("0.25"), Decimal("20"), "CME-arithmetic-reference-v1")
ES_REFERENCE = FuturesTerms("ES", Decimal("0.25"), Decimal("50"), "CME-arithmetic-reference-v1")


def mini_equivalents(delta_usd_per_source_unit: Decimal, receiver_points_per_source_unit: Decimal,
                     receiver: FuturesTerms) -> Fraction:
    """Information feature from an explicit local Jacobian, never order quantity."""
    slope = exact_decimal(receiver_points_per_source_unit)
    if not slope:
        raise DependencyUnavailable("zero mapping Jacobian")
    return Fraction(exact_decimal(delta_usd_per_source_unit)) / (Fraction(slope) * Fraction(receiver.usd_per_point))
