"""Day-start headroom and incremental mark-to-stop reserves (P08)."""

from dataclasses import dataclass
from decimal import Decimal

from trading_research.errors import ContractError
from trading_research.execution.costs import sum_costs
from trading_research.foundations.units import FuturesTerms, Ticks, decimal_product, exact_decimal


@dataclass(frozen=True)
class Exposure:
    instrument: str
    terms: FuturesTerms
    side: int
    current_liquidation: Ticks
    stop: Ticks
    remaining_fees: Decimal
    gap_reserve: Decimal

    def __post_init__(self):
        if self.terms.root not in {"NQ", "ES"} or not self.instrument or type(self.side) is not int or self.side not in {-1, 1}:
            raise ContractError("primary exposure must be one outright NQ/ES mini")
        if any(not isinstance(v, Decimal) or not v.is_finite() or v < 0 for v in (self.remaining_fees, self.gap_reserve)):
            raise ContractError("explicit nonnegative remaining fees and gap reserve required")

    @property
    def incremental_reserve(self) -> Decimal:
        adverse_ticks = max(0, self.side * (self.current_liquidation.value - self.stop.value))
        return sum_costs(decimal_product(adverse_ticks, self.terms.tick_size, self.terms.usd_per_point),
                         self.remaining_fees, self.gap_reserve)


@dataclass(frozen=True)
class RiskVerdict:
    allowed: bool
    daily_headroom: Decimal
    firm_headroom: Decimal | None
    incremental_reserve: Decimal
    reason: str
    halt: bool


def risk_verdict(*, daily_budget: Decimal, trading_net_liquidation_pnl: Decimal,
                 firm_headroom: Decimal | None, mutually_possible_exposures: tuple[Exposure, ...],
                 rule_version: str, state_known: bool) -> RiskVerdict:
    for value in (daily_budget, trading_net_liquidation_pnl):
        exact_decimal(value)
    if not Decimal(0) < daily_budget <= Decimal(1000) or not rule_version:
        raise ContractError("frozen day-start loss objective must be positive and at most 1000 USD")
    if firm_headroom is not None:
        exact_decimal(firm_headroom)
    if not isinstance(mutually_possible_exposures, tuple):
        raise ContractError("enumerate feasible simultaneous exposure/race scenarios explicitly")
    daily = sum_costs(daily_budget, trading_net_liquidation_pnl)
    reserve = sum_costs(*(e.incremental_reserve for e in mutually_possible_exposures))
    if not state_known:
        return RiskVerdict(False, daily, firm_headroom, reserve, "unknown account, position, pending order or quote state", True)
    if daily <= 0 or (firm_headroom is not None and firm_headroom <= 0):
        return RiskVerdict(False, daily, firm_headroom, reserve, "day-start or firm headroom exhausted", True)
    if reserve > daily or (firm_headroom is not None and reserve > firm_headroom):
        return RiskVerdict(False, daily, firm_headroom, reserve, "incremental stop/cost/race reserve exceeds headroom", False)
    return RiskVerdict(True, daily, firm_headroom, reserve, "within both frozen limits", False)
